/**
 * sanitizer.js
 * Sanitizes markdown content for RAG (Retrieval-Augmented Generation)
 * Removes tables, code blocks, checklists while preserving semantic content
 */

class RAGSanitizer {
  /**
   * Remove markdown tables
   * Tables are not suitable for RAG embedding
   * @param {string} content - Markdown content
   * @returns {string} Content without tables
   */
  removeTables(content) {
    let lines = content.split('\n');
    let result = [];
    let inTable = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      // Detect table header (contains | and -)
      const isTableHeader =
        line.includes('|') && 
        line.includes('-') && 
        (i > 0 && lines[i - 1].includes('|'));

      // Table separator line (all dashes and pipes)
      const isSeparator = /^\|[\s\-:|]+\|$/.test(line);

      // Table data row
      const isTableRow = line.startsWith('|') && line.endsWith('|');

      if (isSeparator || isTableRow || isTableHeader) {
        inTable = true;
        // Skip table lines but preserve paragraph continuity
        continue;
      } else if (inTable && line === '') {
        inTable = false;
      }

      if (!inTable) {
        result.push(lines[i]);
      }
    }

    return result.join('\n');
  }

  /**
   * Remove fenced code blocks
   * Code blocks with details are not suitable for RAG
   * Preserves inline code (backticks)
   * @param {string} content - Markdown content
   * @returns {string} Content without code blocks
   */
  removeFencedCodeBlocks(content) {
    // Match triple backticks or triple tildes
    const codeBlockPattern = /```[\s\S]*?```|~~~[\s\S]*?~~~/g;
    return content.replace(codeBlockPattern, '');
  }

  /**
   * Remove checklists and list markers
   * Keeps list content but removes formatting
   * @param {string} content - Markdown content
   * @returns {string} Content without checklist formatting
   */
  removeChecklists(content) {
    let lines = content.split('\n');
    let result = [];

    for (let line of lines) {
      // Remove checkbox patterns: [ ], [x], [X]
      let cleaned = line
        .replace(/^\s*[-*]\s*\[\s*[xX ]?\s*\]\s*/g, '') // List checkbox
        .replace(/\[\s*[xX ]?\s*\]\s*/g, ''); // Inline checkbox

      // Keep the content but remove bullet points for pure text paragraphs
      // However, keep structure for readability
      if (line.trim().match(/^[-*]\s+\[/)) {
        // This was a checklist item, keep as regular bullet
        cleaned = cleaned.trim();
        if (cleaned.length > 0) {
          result.push('• ' + cleaned);
        }
      } else {
        result.push(line);
      }
    }

    return result.join('\n');
  }

  /**
   * Remove metadata blocks and frontmatter
   * @param {string} content - Markdown content
   * @returns {string} Content without metadata blocks
   */
  removeMetadataBlocks(content) {
    // Remove YAML frontmatter (---...---)
    let cleaned = content.replace(/^---[\s\S]*?---\n/m, '');

    // Remove HTML comments
    cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, '');

    return cleaned;
  }

  /**
   * Extract meaningful text from headings and paragraphs
   * Keep structure but remove unnecessary formatting
   * @param {string} content - Markdown content
   * @returns {string} Simplified content
   */
  extractMeaningfulText(content) {
    let lines = content.split('\n');
    let result = [];

    for (let line of lines) {
      // Keep headings (they provide context)
      if (line.trim().startsWith('#')) {
        result.push(line);
      }
      // Skip horizontal rules
      else if (/^[-_*]{3,}$/.test(line.trim())) {
        result.push('');
      }
      // Keep regular text
      else if (line.trim().length > 0) {
        result.push(line);
      }
      // Preserve blank lines for paragraph separation
      else {
        result.push('');
      }
    }

    return result.join('\n');
  }

  /**
   * Remove link markdown but preserve text
   * Converts [text](url) → text
   * @param {string} content - Markdown content
   * @returns {string} Content with link text preserved
   */
  preserveLinkText(content) {
    // Convert markdown links to plain text
    content = content.replace(/\[([^\]]+)\]\([^)]*\)/g, '$1');

    // Convert reference-style links
    content = content.replace(/\[([^\]]+)\]\[.*?\]/g, '$1');

    // Remove link definitions
    content = content.replace(/^\[.*?\]:\s+.*$/gm, '');

    return content;
  }

  /**
   * Remove emphasis markdown but preserve content
   * Converts **text** → text, *text* → text, __text__ → text, _text_ → text
   * @param {string} content - Markdown content
   * @returns {string} Content without emphasis
   */
  removeEmphasisMarkdown(content) {
    // Remove bold/strong
    content = content.replace(/\*\*([^\*]+)\*\*/g, '$1');
    content = content.replace(/__([^_]+)__/g, '$1');

    // Remove italic
    content = content.replace(/\*([^\*]+)\*/g, '$1');
    content = content.replace(/_([^_]+)_/g, '$1');

    // Remove strikethrough
    content = content.replace(/~~([^~]+)~~/g, '$1');

    return content;
  }

  /**
   * Clean up resulting whitespace issues
   * @param {string} content - Markdown content
   * @returns {string} Cleaned content
   */
  normalizeWhitespace(content) {
    // Remove multiple consecutive blank lines
    content = content.replace(/\n\n\n+/g, '\n\n');

    // Trim each line
    let lines = content.split('\n').map(line => line.trim());

    // Remove leading/trailing blank lines
    while (lines.length > 0 && lines[0] === '') {
      lines.shift();
    }
    while (lines.length > 0 && lines[lines.length - 1] === '') {
      lines.pop();
    }

    return lines.join('\n');
  }

  /**
   * Main sanitization pipeline
   * @param {string} content - Markdown content
   * @returns {string} RAG-ready content
   */
  sanitize(content) {
    if (!content || typeof content !== 'string') {
      return '';
    }

    // Step 1: Remove metadata blocks
    let sanitized = this.removeMetadataBlocks(content);

    // Step 2: Remove code blocks
    sanitized = this.removeFencedCodeBlocks(sanitized);

    // Step 3: Remove tables
    sanitized = this.removeTables(sanitized);

    // Step 4: Remove checklists
    sanitized = this.removeChecklists(sanitized);

    // Step 5: Preserve link text (remove markdown)
    sanitized = this.preserveLinkText(sanitized);

    // Step 6: Remove emphasis markdown
    sanitized = this.removeEmphasisMarkdown(sanitized);

    // Step 7: Extract meaningful text (simplify)
    sanitized = this.extractMeaningfulText(sanitized);

    // Step 8: Normalize whitespace
    sanitized = this.normalizeWhitespace(sanitized);

    return sanitized;
  }

  /**
   * Get sanitization statistics
   * @param {string} original - Original content
   * @param {string} sanitized - Sanitized content
   * @returns {Object} Statistics object
   */
  getStats(original, sanitized) {
    return {
      originalLength: original.length,
      sanitizedLength: sanitized.length,
      reducePercentage: Math.round(
        ((original.length - sanitized.length) / original.length) * 100
      ),
      removedLength: original.length - sanitized.length
    };
  }
}

module.exports = RAGSanitizer;
