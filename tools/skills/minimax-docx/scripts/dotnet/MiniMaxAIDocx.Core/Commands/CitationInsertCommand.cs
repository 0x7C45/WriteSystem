using System.CommandLine;
using System.Text.Json;
using System.Text.RegularExpressions;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

namespace MiniMaxAIDocx.Core.Commands;

/// <summary>
/// Batch-inserts citation markers [N] into an existing DOCX at specific paragraph positions
/// from a citation_plan.jsonl file. Preserves all existing run formatting (rPr).
/// </summary>
public static class CitationInsertCommand
{
    public static Command Create()
    {
        var inputOpt = new Option<string>("--input") { Description = "Input DOCX file", Required = true };
        var outputOpt = new Option<string>("--output") { Description = "Output file path (defaults to overwriting input)" };
        var planOpt = new Option<string>("--plan") { Description = "citation_plan.jsonl path", Required = true };
        var thresholdOpt = new Option<double>("--threshold") { Description = "Minimum confidence to apply (0-1)" };
        thresholdOpt.DefaultValueFactory = _ => 0.80;
        var superscriptOpt = new Option<bool>("--superscript") { Description = "Format citation markers as superscript" };
        var dryRunOpt = new Option<bool>("--dry-run") { Description = "Preview insertions without writing" };
        var validateOpt = new Option<bool>("--validate") { Description = "Run post-insertion validation" };

        var cmd = new Command("insert-citations", "Batch-insert citation markers from a JSONL plan")
        {
            inputOpt, outputOpt, planOpt, thresholdOpt, superscriptOpt, dryRunOpt, validateOpt
        };

        cmd.SetAction((parseResult) =>
        {
            var input = parseResult.GetValue(inputOpt)!;
            var output = parseResult.GetValue(outputOpt) ?? input;
            var planPath = parseResult.GetValue(planOpt)!;
            var threshold = parseResult.GetValue(thresholdOpt);
            var superscript = parseResult.GetValue(superscriptOpt);
            var dryRun = parseResult.GetValue(dryRunOpt);
            var validate = parseResult.GetValue(validateOpt);

            if (!File.Exists(input))
            {
                Console.Error.WriteLine($"Input file not found: {input}");
                return;
            }

            if (!File.Exists(planPath))
            {
                Console.Error.WriteLine($"Plan file not found: {planPath}");
                return;
            }

            var planEntries = ParseCitationPlan(planPath, threshold);
            if (planEntries.Count == 0)
            {
                Console.WriteLine("[insert-citations] No entries to apply.");
                return;
            }

            // Group insertions by paragraph index, sorted reverse by offset
            var grouped = planEntries
                .GroupBy(e => e.ParaId)
                .ToDictionary(
                    g => g.Key,
                    g => g.SelectMany(e => e.Insertions)
                         .OrderByDescending(i => i.CharOffset)
                         .ToList()
                );

            Console.WriteLine($"[insert-citations] Plan loaded: {planEntries.Count} entries, " +
                              $"{grouped.Count} paragraphs, threshold={threshold}");

            if (dryRun)
            {
                Console.WriteLine("[insert-citations] DRY RUN — no files will be modified.\n");
                PrintDryRun(input, grouped);
                return;
            }

            // Copy input to output
            if (output != input)
                File.Copy(input, output, overwrite: true);

            // Open and process
            using var doc = WordprocessingDocument.Open(output, true);
            var body = doc.MainDocumentPart?.Document.Body;
            if (body == null)
            {
                Console.Error.WriteLine("No document body found.");
                return;
            }

            var paragraphs = body.Elements<Paragraph>().ToList();
            int totalInserted = 0;
            int totalSkipped = 0;
            int paragraphsTouched = 0;

            foreach (var (paraId, insertions) in grouped)
            {
                // Plan uses 1-based paragraph IDs
                int zeroIndex = paraId - 1;
                if (zeroIndex < 0 || zeroIndex >= paragraphs.Count)
                {
                    Console.Error.WriteLine($"Warning: paragraph {paraId} out of range (1..{paragraphs.Count}), skipped.");
                    continue;
                }

                var para = paragraphs[zeroIndex];
                var paraText = GetParagraphText(para);

                foreach (var ins in insertions)
                {
                    // Dedup: check if marker already exists near target offset
                    if (IsDuplicate(paraText, ins.CharOffset, ins.Text))
                    {
                        totalSkipped++;
                        continue;
                    }

                    InsertAtOffset(para, ins.CharOffset, ins.Text, superscript);
                    totalInserted++;
                    paragraphsTouched++;

                    // Refresh paragraph text after modification
                    paraText = GetParagraphText(para);
                }
            }

            doc.MainDocumentPart!.Document.Save();
            doc.Dispose(); // Release file handle before validation

            var summary = new
            {
                input,
                output,
                plan_entries = planEntries.Count,
                paragraphs_touched = grouped.Count,
                insertions_applied = totalInserted,
                duplicates_skipped = totalSkipped,
            };

            Console.WriteLine($"[insert-citations] Done: {totalInserted} inserted, " +
                              $"{totalSkipped} skipped, {grouped.Count} paragraphs touched.");
            Console.WriteLine($"[insert-citations] Output: {output}");

            // Post-insertion validation
            if (validate)
            {
                RunValidation(output, planEntries);
            }
        });

        return cmd;
    }

    // ── Data model ──────────────────────────────────────────────────────

    private sealed record CitationPlanEntry
    {
        public int ParaId { get; init; }
        public string Chapter { get; init; } = "";
        public string Status { get; init; } = "";
        public double Confidence { get; init; }
        public List<CitationInsertion> Insertions { get; init; } = new();
    }

    private sealed record CitationInsertion
    {
        public int CharOffset { get; init; }
        public string Text { get; init; } = "";
        public List<int> CitationIds { get; init; } = new();
    }

    // ── Plan parsing ────────────────────────────────────────────────────

    private static List<CitationPlanEntry> ParseCitationPlan(string planPath, double threshold)
    {
        var entries = new List<CitationPlanEntry>();

        using var reader = new StreamReader(planPath);
        string? line;
        while ((line = reader.ReadLine()) != null)
        {
            line = line.Trim();
            if (string.IsNullOrEmpty(line)) continue;

            try
            {
                using var doc = JsonDocument.Parse(line);
                var root = doc.RootElement;

                string status = root.TryGetProperty("status", out var statusProp)
                    ? statusProp.GetString() ?? ""
                    : "proposed";

                double confidence = root.TryGetProperty("confidence", out var confProp)
                    ? confProp.GetDouble()
                    : 1.0;

                // Only apply proposed entries above threshold
                if (status != "proposed" || confidence < threshold)
                    continue;

                int paraId = root.GetProperty("docx_para_id").GetInt32();
                string chapter = root.TryGetProperty("chapter", out var chProp)
                    ? chProp.GetString() ?? ""
                    : "";

                var insertions = new List<CitationInsertion>();
                if (root.TryGetProperty("insertions", out var insArr))
                {
                    foreach (var insEl in insArr.EnumerateArray())
                    {
                        insertions.Add(new CitationInsertion
                        {
                            CharOffset = insEl.GetProperty("char_offset").GetInt32(),
                            Text = insEl.TryGetProperty("text", out var textProp)
                                ? textProp.GetString() ?? ""
                                : "",
                            CitationIds = insEl.TryGetProperty("citation_ids", out var idsProp)
                                ? idsProp.EnumerateArray().Select(id => id.GetInt32()).ToList()
                                : new List<int>(),
                        });
                    }
                }

                entries.Add(new CitationPlanEntry
                {
                    ParaId = paraId,
                    Chapter = chapter,
                    Status = status,
                    Confidence = confidence,
                    Insertions = insertions,
                });
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Warning: skipping malformed plan line: {ex.Message}");
            }
        }

        return entries;
    }

    // ── Core insertion algorithm ────────────────────────────────────────

    /// <summary>
    /// Inserts text at a specific character offset within a paragraph,
    /// preserving all existing run formatting (rPr) by splitting the target run
    /// into before/citation/after segments.
    /// </summary>
    private static void InsertAtOffset(Paragraph paragraph, int charOffset, string text, bool superscript)
    {
        var runs = paragraph.Elements<Run>().ToList();
        if (runs.Count == 0)
        {
            // No runs exist — create a new one with default formatting
            var newRun = CreateCitationRun(text, superscript, null);
            paragraph.Append(newRun);
            return;
        }

        // Clamp offset
        int totalLen = runs.Sum(r => r.Elements<Text>().Sum(t => (t.Text?.Length) ?? 0));
        charOffset = Math.Max(0, Math.Min(charOffset, totalLen));

        // Build character-to-run map to find the target run and local offset
        int cursor = 0;
        Run? targetRun = null;
        int offsetInRun = 0;

        foreach (var run in runs)
        {
            var runLen = run.Elements<Text>().Sum(t => (t.Text?.Length) ?? 0);

            if (cursor + runLen > charOffset || cursor + runLen == charOffset)
            {
                // Target offset is within this run (or at its boundary)
                targetRun = run;
                offsetInRun = charOffset - cursor;
                break;
            }

            cursor += runLen;
        }

        // Fallback: if offset is at the very end, use the last run
        targetRun ??= runs[^1];
        if (targetRun == null) return;

        var runTextElements = targetRun.Elements<Text>().ToList();
        int localCursor = 0;

        // Find the exact Text element and position within it
        foreach (var textElem in runTextElements)
        {
            int segLen = textElem.Text?.Length ?? 0;

            if (localCursor + segLen > offsetInRun)
            {
                int splitAt = offsetInRun - localCursor;
                string before = (textElem.Text ?? "")[..splitAt];
                string after = (textElem.Text ?? "")[splitAt..];

                // Modify the original Text element to contain only "before"
                textElem.Text = before;
                if (before.Length > 0 && (before.StartsWith(' ') || before.EndsWith(' ')))
                    textElem.Space = SpaceProcessingModeValues.Preserve;

                // Create citation run inheriting source formatting
                var citationRun = CreateCitationRun(text, superscript, targetRun.RunProperties);

                // Create continuation run for "after" text, cloning source rPr
                var afterRun = new Run();
                if (targetRun.RunProperties != null)
                {
                    afterRun.RunProperties = (RunProperties)targetRun.RunProperties.CloneNode(true);
                }
                var afterText = new Text(after)
                {
                    Space = (after.Length > 0 && (after.StartsWith(' ') || after.EndsWith(' ')))
                        ? SpaceProcessingModeValues.Preserve
                        : SpaceProcessingModeValues.Default
                };
                afterRun.Append(afterText);

                // Insert: targetRun | citationRun | afterRun
                targetRun.InsertAfterSelf(citationRun);
                citationRun.InsertAfterSelf(afterRun);
                return;
            }

            // offsetInRun falls exactly at the boundary between Text elements
            if (localCursor + segLen == offsetInRun && offsetInRun > 0)
            {
                // Insert citation after this Text element (still within same Run)
                // We need to split: everything before this point stays, citation goes after,
                // then continuation
                // Actually, since offsetInRun == localCursor + segLen, the insertion point
                // is right after this text element. Insert a new run after the current run.

                var citationRun = CreateCitationRun(text, superscript, targetRun.RunProperties);
                targetRun.InsertAfterSelf(citationRun);
                return;
            }

            localCursor += segLen;
        }

        // If we didn't find an insertion point inside any Text element,
        // append to the end of the target run
        var finalCitation = CreateCitationRun(text, superscript, targetRun.RunProperties);
        targetRun.InsertAfterSelf(finalCitation);
    }

    /// <summary>
    /// Creates a new Run for a citation marker, optionally inheriting formatting
    /// from a source run and applying superscript.
    /// </summary>
    private static Run CreateCitationRun(string text, bool superscript, RunProperties? inheritFrom)
    {
        var run = new Run();

        if (inheritFrom != null)
        {
            // Clone source formatting, then strip bold/italic for citation marker
            run.RunProperties = (RunProperties)inheritFrom.CloneNode(true);

            // Remove bold
            var bold = run.RunProperties.ChildElements
                .FirstOrDefault(e => e is Bold || e.LocalName == "b");
            if (bold != null) run.RunProperties.RemoveChild(bold);

            // Remove italic
            var italic = run.RunProperties.ChildElements
                .FirstOrDefault(e => e is Italic || e.LocalName == "i");
            if (italic != null) run.RunProperties.RemoveChild(italic);

            // Remove highlight
            var highlight = run.RunProperties.ChildElements
                .FirstOrDefault(e => e.LocalName == "highlight");
            if (highlight != null) run.RunProperties.RemoveChild(highlight);
        }

        // Apply superscript if requested
        if (superscript)
        {
            run.RunProperties ??= new RunProperties();
            run.RunProperties.VerticalTextAlignment = new VerticalTextAlignment
            {
                Val = VerticalPositionValues.Superscript
            };
        }

        var textElem = new Text(text) { Space = SpaceProcessingModeValues.Preserve };
        run.Append(textElem);
        return run;
    }

    // ── Helpers ─────────────────────────────────────────────────────────

    private static string GetParagraphText(Paragraph paragraph)
    {
        return string.Concat(
            paragraph.Descendants<Text>()
                .Select(t => t.Text ?? "")
        );
    }

    private static bool IsDuplicate(string paragraphText, int offset, string marker)
    {
        if (string.IsNullOrEmpty(paragraphText) || string.IsNullOrEmpty(marker))
            return false;

        int windowStart = Math.Max(0, offset - 6);
        int windowEnd = Math.Min(paragraphText.Length, offset + 6 + marker.Length);

        if (windowEnd > paragraphText.Length || windowStart >= windowEnd)
            return false;

        string window = paragraphText[windowStart..windowEnd];
        return window.Contains(marker);
    }

    // ── Dry run output ──────────────────────────────────────────────────

    private static void PrintDryRun(string inputDocx, Dictionary<int, List<CitationInsertion>> grouped)
    {
        using var doc = WordprocessingDocument.Open(inputDocx, false);
        var body = doc.MainDocumentPart?.Document.Body;
        if (body == null) return;

        var paragraphs = body.Elements<Paragraph>().ToList();
        int count = 0;

        foreach (var (paraId, insertions) in grouped.OrderBy(kv => kv.Key))
        {
            int zeroIndex = paraId - 1;
            if (zeroIndex < 0 || zeroIndex >= paragraphs.Count) continue;

            var para = paragraphs[zeroIndex];
            var paraText = GetParagraphText(para);
            var preview = paraText.Length > 80 ? paraText[..80] + "..." : paraText;

            Console.WriteLine($"  Para {paraId}: \"{preview}\"");
            foreach (var ins in insertions.OrderBy(i => i.CharOffset))
            {
                int contextStart = Math.Max(0, ins.CharOffset - 15);
                int contextEnd = Math.Min(paraText.Length, ins.CharOffset + 15);
                string before = paraText[contextStart..ins.CharOffset];
                string after = paraText[ins.CharOffset..contextEnd];
                Console.WriteLine($"    + offset {ins.CharOffset}: \"{before}|{ins.Text}|{after}\"");
                count++;
            }
        }

        Console.WriteLine($"\n  Total: {count} insertions across {grouped.Count} paragraphs");
    }

    // ── Validation ──────────────────────────────────────────────────────

    private static void RunValidation(string docxPath, List<CitationPlanEntry> plan)
    {
        Console.WriteLine("\n[insert-citations] Running validation...");

        using var doc = WordprocessingDocument.Open(docxPath, false);
        var body = doc.MainDocumentPart?.Document.Body;
        if (body == null)
        {
            Console.Error.WriteLine("[validation] No document body found.");
            return;
        }

        var paragraphs = body.Elements<Paragraph>().ToList();

        // Count citation markers in body text (exclude references section)
        var markerPattern = new Regex(@"\[(\d{1,3})\]");
        int totalMarkers = 0;
        var markerIds = new HashSet<int>();

        foreach (var para in paragraphs)
        {
            var text = GetParagraphText(para);
            // Skip paragraphs that look like reference entries: "[1] Author..."
            if (Regex.IsMatch(text, @"^\s*\[\d{1,3}\]\s+\S"))
                continue;

            foreach (Match m in markerPattern.Matches(text))
            {
                if (int.TryParse(m.Groups[1].Value, out int id) && id > 0)
                {
                    totalMarkers++;
                    markerIds.Add(id);
                }
            }
        }

        // Expected markers from plan
        var expectedIds = new HashSet<int>();
        int expectedCount = 0;
        foreach (var entry in plan)
        {
            foreach (var ins in entry.Insertions)
            {
                expectedCount++;
                foreach (var id in ins.CitationIds)
                    expectedIds.Add(id);
            }
        }

        var missing = expectedIds.Except(markerIds).OrderBy(x => x).ToList();
        var extra = markerIds.Except(expectedIds).OrderBy(x => x).ToList();

        Console.WriteLine($"  Paragraphs in DOCX: {paragraphs.Count}");
        Console.WriteLine($"  Citation markers found: {totalMarkers}");
        Console.WriteLine($"  Unique reference IDs: [{string.Join(", ", markerIds.OrderBy(x => x))}]");
        Console.WriteLine($"  Expected from plan: {expectedCount} insertions, {expectedIds.Count} unique IDs");

        if (missing.Count > 0)
            Console.WriteLine($"  MISSING IDs: [{string.Join(", ", missing)}]");
        if (extra.Count > 0)
            Console.WriteLine($"  EXTRA IDs: [{string.Join(", ", extra)}]");
        if (missing.Count == 0 && extra.Count == 0)
            Console.WriteLine("  Citation coverage: ALL EXPECTED IDS PRESENT");
    }
}
