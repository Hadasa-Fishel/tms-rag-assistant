/**
 * metadata.js
 * Extracts and generates metadata for chunks
 * Type mapping, source detection, date extraction, ID generation
 */

class MetadataExtractor {
  constructor() {
    // Type mapping based on file names
    this.typeMapping = {
      'instructions.md': 'instruction',
      'planning.md': 'plan',
      'system_spec.md': 'spec',
      'db_changes.md': 'spec',
      'ui_guidelines.md': 'instruction',
      'install_guide.md': 'instruction',
      'technical_constraints.md': 'spec',
      'install_notes.md': 'instruction'
    };

    // Counter for sequential ID generation
    this.idCounters = {};
  }

  /**
   * Determine content type from filename
   * @param {string} fileName - Name of file
   * @returns {string} Content type
   */
  getType(fileName) {
    return this.typeMapping[fileName] || 'general';
  }

  /**
   * Determine source from file origin
   * Files from cursor_docs or claude_docs
   * @param {Object} fileMetadata - File metadata object
   * @returns {string} Source label
   */
  getSource(fileMetadata) {
    // fileMetadata should have a 'source' field from fileManager
    return fileMetadata.source || 'Unknown';
  }

  /**
   * Extract date from content
   * Looks for date patterns: "2026-02-XX" or "Last Updated: 2026-02-XX"
   * @param {string} content - Markdown content
   * @returns {string} ISO date string or current date
   */
  extractDate(content) {
    if (!content || typeof content !== 'string') {
      return new Date().toISOString().split('T')[0];
    }

    // Pattern 1: Direct date in YYYY-MM-DD format
    const datePattern = /(\d{4}-\d{2}-\d{2})/;
    const match = content.match(datePattern);

    if (match) {
      const dateStr = match[1];
      // Validate it's a real date
      const date = new Date(dateStr + 'T00:00:00Z');
      if (!isNaN(date.getTime())) {
        return dateStr;
      }
    }

    // Pattern 2: "Last Updated:" or similar
    const updatedPattern = /(?:Last\s+Updated|Updated|Date):\s*(\d{4}-\d{2}-\d{2})/i;
    const updatedMatch = content.match(updatedPattern);

    if (updatedMatch) {
      const dateStr = updatedMatch[1];
      const date = new Date(dateStr + 'T00:00:00Z');
      if (!isNaN(date.getTime())) {
        return dateStr;
      }
    }

    // Default to current date
    return new Date().toISOString().split('T')[0];
  }

  /**
   * Generate unique chunk ID
   * Format: [source]-[type]-[number]
   * Example: cursor-spec-001
   * @param {string} source - Source (Cursor or Claude)
   * @param {string} type - Type (instruction, plan, spec)
   * @returns {string} Unique ID
   */
  generateId(source, type) {
    const key = `${source.toLowerCase()}-${type}`;

    if (!this.idCounters[key]) {
      this.idCounters[key] = 0;
    }

    this.idCounters[key]++;
    const num = String(this.idCounters[key]).padStart(3, '0');

    return `${key}-${num}`;
  }

  /**
   * Extract all metadata for a chunk
   * @param {Object} chunk - Chunk object with content, fileName, etc
   * @param {Object} fileMetadata - Original file metadata
   * @returns {Object} Complete chunk with metadata
   */
  enrich(chunk, fileMetadata) {
    const fileName = fileMetadata.fileName;
    const source = this.getSource(fileMetadata);
    const type = this.getType(fileName);
    const date = this.extractDate(chunk.content);

    const id = this.generateId(source, type);

    return {
      id,
      type,
      source,
      date,
      fileName,
      title: chunk.title || '',
      content: chunk.content,
      wordCount: chunk.wordCount,
      chunkIndex: chunk.chunkIndex || 0,
      chunkCount: chunk.chunkCount || 1,
      createdAt: new Date().toISOString()
    };
  }

  /**
   * Extract key topics/entities from chunk
   * Simple keyword extraction based on headings and frequency
   * @param {string} content - Chunk content
   * @returns {Array} Array of topic strings
   */
  extractTopics(content) {
    const topics = [];

    // Extract heading text as topics
    const headings = content.match(/^##\s+(.+)$/gm) || [];
    headings.forEach(heading => {
      const text = heading.replace(/^##\s+/, '').trim();
      if (text && topics.indexOf(text) === -1) {
        topics.push(text);
      }
    });

    // Extract common technical terms (case-insensitive)
    const technicalTerms = [
      'database', 'api', 'authentication', 'performance', 'security',
      'deployment', 'migration', 'testing', 'monitoring', 'scaling',
      'caching', 'websocket', 'task', 'user', 'workflow', 'integration'
    ];

    const contentLower = content.toLowerCase();
    technicalTerms.forEach(term => {
      if (contentLower.includes(term) && topics.indexOf(term) === -1) {
        topics.push(term);
      }
    });

    return topics.slice(0, 10); // Limit to top 10 topics
  }

  /**
   * Validate metadata
   * @param {Object} metadata - Metadata object to validate
   * @returns {Object} Validation result
   */
  validate(metadata) {
    const issues = [];

    if (!metadata.id) issues.push('Missing id');
    if (!metadata.type) issues.push('Missing type');
    if (!metadata.source) issues.push('Missing source');
    if (!metadata.date) issues.push('Missing date');
    if (!metadata.fileName) issues.push('Missing fileName');
    if (!metadata.content) issues.push('Missing content');

    const isValid = issues.length === 0;

    return {
      isValid,
      issues,
      metadata
    };
  }

  /**
   * Generate metadata summary
   * @param {Array} chunks - Array of enriched chunks
   * @returns {Object} Summary object
   */
  generateSummary(chunks) {
    const summary = {
      totalChunks: chunks.length,
      byType: {},
      bySource: {},
      byFile: {},
      dateRange: {
        earliest: null,
        latest: null
      },
      totalWords: 0
    };

    for (let chunk of chunks) {
      // Count by type
      summary.byType[chunk.type] = (summary.byType[chunk.type] || 0) + 1;

      // Count by source
      summary.bySource[chunk.source] = (summary.bySource[chunk.source] || 0) + 1;

      // Count by file
      summary.byFile[chunk.fileName] = (summary.byFile[chunk.fileName] || 0) + 1;

      // Track date range
      if (!summary.dateRange.earliest || chunk.date < summary.dateRange.earliest) {
        summary.dateRange.earliest = chunk.date;
      }
      if (!summary.dateRange.latest || chunk.date > summary.dateRange.latest) {
        summary.dateRange.latest = chunk.date;
      }

      // Count total words
      summary.totalWords += chunk.wordCount || 0;
    }

    return summary;
  }

  /**
   * Reset ID counters
   * Useful for testing
   */
  resetIdCounters() {
    this.idCounters = {};
  }
}

module.exports = MetadataExtractor;
