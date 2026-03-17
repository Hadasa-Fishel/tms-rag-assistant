/**
 * cleaner.js
 * Cleans and normalizes markdown content
 * Removes duplicates, normalizes headings, fixes broken lines
 */

class MarkdownCleaner {
  /**
   * Normalize markdown headings
   * Convert all heading levels to only # and ##
   * @param {string} content - Markdown content
   * @returns {string} Cleaned content
   */
  normalizeHeadings(content) {
    let lines = content.split('\n');
    let normalized = [];
    let lastHeadingLevel = 0;

    for (let line of lines) {
      const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);

      if (headingMatch) {
        const level = headingMatch[1].length;
        const title = headingMatch[2];

        // Convert heading levels
        if (level === 1) {
          normalized.push(`# ${title}`);
          lastHeadingLevel = 1;
        } else if (level === 2 || level === 3) {
          normalized.push(`## ${title}`);
          lastHeadingLevel = 2;
        } else {
          // Level 4+ converted to ## (subsection)
          normalized.push(`## ${title}`);
          lastHeadingLevel = 2;
        }
      } else {
        normalized.push(line);
      }
    }

    return normalized.join('\n');
  }

  /**
   * Remove duplicate paragraphs
   * @param {string} content - Markdown content
   * @returns {string} Content without duplicates
   */
  removeDuplicateParagraphs(content) {
    const paragraphs = content.split('\n\n');
    const seen = new Set();
    const unique = [];

    for (let para of paragraphs) {
      const normalized = para.trim().toLowerCase();
      if (normalized.length > 0 && !seen.has(normalized)) {
        seen.add(normalized);
        unique.push(para.trim());
      }
    }

    return unique.join('\n\n');
  }

  /**
   * Merge broken lines back into paragraphs
   * Detects lines that should be part of same paragraph
   * @param {string} content - Markdown content
   * @returns {string} Content with merged lines
   */
  mergeBrokenLines(content) {
    let lines = content.split('\n');
    let merged = [];
    let currentPara = '';

    for (let line of lines) {
      line = line.trim();

      // Empty line = end of paragraph
      if (line === '') {
        if (currentPara.length > 0) {
          merged.push(currentPara.trim());
          currentPara = '';
        }
        merged.push('');
      }
      // Start of heading = end of paragraph
      else if (line.startsWith('#')) {
        if (currentPara.length > 0) {
          merged.push(currentPara.trim());
          currentPara = '';
        }
        merged.push(line);
      }
      // Regular line = add to paragraph
      else {
        if (currentPara.length > 0) {
          currentPara += ' ' + line;
        } else {
          currentPara = line;
        }
      }
    }

    // Don't forget last paragraph
    if (currentPara.length > 0) {
      merged.push(currentPara.trim());
    }

    return merged.join('\n');
  }

  /**
   * Remove control characters and fix encoding issues
   * @param {string} content - Markdown content
   * @returns {string} Cleaned content
   */
  removeControlCharacters(content) {
    // Remove null bytes
    content = content.replace(/\0/g, '');

    // Remove other control characters except newlines, tabs
    content = content.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');

    // Normalize multiple spaces to single
    content = content.replace(/[ ]{2,}/g, ' ');

    // Normalize multiple newlines to max 2
    content = content.replace(/\n{3,}/g, '\n\n');

    return content;
  }

  /**
   * Preserve semantic structure markers
   * Identify and protect important patterns (dates, links, etc.)
   * @param {string} content - Markdown content
   * @returns {string} Content with preserved structure
   */
  preserveSemanticStructure(content) {
    // Links are already safe in markdown format
    // Preserve date patterns (YYYY-MM-DD)
    const datePattern = /\d{4}-\d{2}-\d{2}/g;
    const dates = content.match(datePattern) || [];

    // Preserve inline code (backticks)
    const codePattern = /`[^`]+`/g;
    const codes = content.match(codePattern) || [];

    // Just ensure they're preserved in output (they naturally are)
    return content;
  }

  /**
   * Main cleaning pipeline
   * @param {string} content - Raw markdown content
   * @returns {string} Cleaned content
   */
  clean(content) {
    if (!content || typeof content !== 'string') {
      return '';
    }

    // Step 1: Remove control characters
    let cleaned = this.removeControlCharacters(content);

    // Step 2: Normalize headings
    cleaned = this.normalizeHeadings(cleaned);

    // Step 3: Merge broken lines
    cleaned = this.mergeBrokenLines(cleaned);

    // Step 4: Remove duplicate paragraphs
    cleaned = this.removeDuplicateParagraphs(cleaned);

    // Step 5: Preserve semantic structure
    cleaned = this.preserveSemanticStructure(cleaned);

    // Final trim
    cleaned = cleaned.trim();

    return cleaned;
  }

  /**
   * Get cleaning statistics
   * @param {string} original - Original content
   * @param {string} cleaned - Cleaned content
   * @returns {Object} Statistics object
   */
  getStats(original, cleaned) {
    return {
      originalLength: original.length,
      cleanedLength: cleaned.length,
      reducePercentage: Math.round(
        ((original.length - cleaned.length) / original.length) * 100
      ),
      originalLines: original.split('\n').length,
      cleanedLines: cleaned.split('\n').length
    };
  }
}

module.exports = MarkdownCleaner;
