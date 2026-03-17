/**
 * chunker.js
 * Splits content into logical chunks for RAG
 * Respects section boundaries and word count constraints
 */

class ContentChunker {
  constructor(minWords = 300, maxWords = 800) {
    this.minWords = minWords;
    this.maxWords = maxWords;
  }

  /**
   * Count words in text
   * @param {string} text - Text to count
   * @returns {number} Word count
   */
  countWords(text) {
    return text
      .trim()
      .split(/\s+/)
      .filter(word => word.length > 0).length;
  }

  /**
   * Extract sections from content
   * Sections are separated by ## headings
   * @param {string} content - Markdown content
   * @returns {Array} Array of section objects
   */
  extractSections(content) {
    const lines = content.split('\n');
    const sections = [];
    let currentSection = null;

    for (let line of lines) {
      // Check if this is a ## heading
      if (line.startsWith('##') && !line.startsWith('###')) {
        // Save previous section if exists
        if (currentSection) {
          sections.push(currentSection);
        }

        // Start new section
        currentSection = {
          title: line.replace(/^##\s+/, '').trim(),
          content: [line],
          depth: 2
        };
      } else if (currentSection) {
        currentSection.content.push(line);
      }
    }

    // Add last section
    if (currentSection) {
      sections.push(currentSection);
    }

    return sections;
  }

  /**
   * Split paragraph into sentences
   * @param {string} paragraph - Paragraph text
   * @returns {Array} Array of sentences
   */
  splitSentences(paragraph) {
    // Split by common sentence endings
    const sentences = paragraph.match(/[^.!?]+[.!?]+/g) || [paragraph];
    return sentences.map(s => s.trim()).filter(s => s.length > 0);
  }

  /**
   * Split section into chunks if too large
   * @param {Object} section - Section object
   * @returns {Array} Array of chunk objects
   */
  splitLargeSection(section) {
    const chunks = [];
    const contentText = section.content.join('\n');
    const wordCount = this.countWords(contentText);

    // If section is already within bounds, return as single chunk
    if (wordCount >= this.minWords && wordCount <= this.maxWords) {
      return [
        {
          title: section.title,
          content: contentText,
          wordCount: wordCount,
          type: 'section'
        }
      ];
    }

    // If too long, split by paragraphs
    if (wordCount > this.maxWords) {
      return this.splitByParagraph(section);
    }

    // If too short, mark for merging
    return [
      {
        title: section.title,
        content: contentText,
        wordCount: wordCount,
        type: 'section',
        tooSmall: true
      }
    ];
  }

  /**
   * Split section by paragraphs
   * @param {Object} section - Section object
   * @returns {Array} Array of chunk objects
   */
  splitByParagraph(section) {
    const chunks = [];
    let currentChunk = [section.title];
    let currentWords = this.countWords(section.title);

    for (let line of section.content.slice(1)) {
      // Skip heading line
      if (line.startsWith('##')) continue;

      const lineWords = this.countWords(line);

      // If adding this line would exceed limit, save chunk
      if (currentWords + lineWords > this.maxWords && currentChunk.length > 1) {
        chunks.push({
          title: section.title,
          content: currentChunk.join('\n'),
          wordCount: currentWords,
          type: 'section-part'
        });
        currentChunk = [section.title];
        currentWords = this.countWords(section.title);
      }

      currentChunk.push(line);
      currentWords += lineWords;
    }

    // Add final chunk
    if (currentChunk.length > 1) {
      chunks.push({
        title: section.title,
        content: currentChunk.join('\n'),
        wordCount: currentWords,
        type: 'section-part'
      });
    }

    return chunks;
  }

  /**
   * Merge small chunks together
   * @param {Array} chunks - Array of chunks
   * @returns {Array} Merged chunks
   */
  mergeSmallChunks(chunks) {
    if (chunks.length === 0) return chunks;

    const merged = [];
    let buffer = null;

    for (let chunk of chunks) {
      // If chunk is too small
      if (chunk.tooSmall || chunk.wordCount < this.minWords) {
        if (!buffer) {
          buffer = { ...chunk };
        } else {
          // Merge with buffer
          buffer.content += '\n\n' + chunk.content;
          buffer.wordCount += chunk.wordCount;

          // If merged chunk is now big enough, add to results
          if (buffer.wordCount >= this.minWords) {
            merged.push({
              ...buffer,
              tooSmall: false
            });
            buffer = null;
          }
        }
      } else {
        // Chunk is appropriate size
        if (buffer) {
          // Merge buffer with this chunk
          buffer.content += '\n\n' + chunk.content;
          buffer.wordCount += chunk.wordCount;
          merged.push({
            ...buffer,
            tooSmall: false
          });
          buffer = null;
        }
        merged.push(chunk);
      }
    }

    // Don't forget remaining buffer
    if (buffer) {
      merged.push(buffer);
    }

    return merged;
  }

  /**
   * Main chunking pipeline
   * @param {string} content - Content to chunk
   * @param {string} fileName - Original file name
   * @returns {Array} Array of chunk objects
   */
  chunk(content, fileName) {
    if (!content || typeof content !== 'string') {
      return [];
    }

    // Step 1: Extract sections
    const sections = this.extractSections(content);

    // Step 2: Split large sections
    let chunks = [];
    for (let section of sections) {
      const sectionChunks = this.splitLargeSection(section);
      chunks.push(...sectionChunks);
    }

    // Step 3: Merge small chunks
    chunks = this.mergeSmallChunks(chunks);

    // Step 4: Add metadata
    chunks = chunks.map((chunk, index) => ({
      ...chunk,
      fileName: fileName,
      chunkIndex: index,
      chunkCount: chunks.length
    }));

    return chunks;
  }

  /**
   * Get chunking statistics
   * @param {Array} chunks - Array of chunks
   * @returns {Object} Statistics object
   */
  getStats(chunks) {
    if (chunks.length === 0) {
      return {
        totalChunks: 0,
        averageWords: 0,
        minWords: 0,
        maxWords: 0,
        totalWords: 0
      };
    }

    const wordCounts = chunks.map(c => c.wordCount);
    const totalWords = wordCounts.reduce((a, b) => a + b, 0);

    return {
      totalChunks: chunks.length,
      averageWords: Math.round(totalWords / chunks.length),
      minWords: Math.min(...wordCounts),
      maxWords: Math.max(...wordCounts),
      totalWords: totalWords,
      chunksInRange: chunks.filter(
        c => c.wordCount >= this.minWords && c.wordCount <= this.maxWords
      ).length
    };
  }
}

module.exports = ContentChunker;
