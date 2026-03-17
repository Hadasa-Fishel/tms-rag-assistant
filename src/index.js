
const path = require('path');
const FileManager = require('./fileManager');
const MarkdownCleaner = require('./cleaner');
const RAGSanitizer = require('./sanitizer');
const ContentChunker = require('./chunker');
const MetadataExtractor = require('./metadata');

class KnowledgeBasePipeline {
  constructor() {
    this.fileManager = null;
    this.cleaner = new MarkdownCleaner();
    this.sanitizer = new RAGSanitizer();
    this.chunker = new ContentChunker(300, 800); // 300-800 words per chunk
    this.metadata = new MetadataExtractor();
    this.allChunks = [];
    this.stats = {};
  }

  /**
   * Initialize pipeline with source and target directories
   */
  async initialize() {
    const projectRoot = path.resolve(__dirname, '..');

    const sourceDirs = {
      [path.join(projectRoot, 'cursor_docs')]: 'Cursor',
      [path.join(projectRoot, 'claude_docs')]: 'Claude'
    };

    const targetDirs = {
      raw: path.join(projectRoot, 'knowledge', 'raw'),
      cleaned: path.join(projectRoot, 'knowledge', 'cleaned'),
      chunks: path.join(projectRoot, 'knowledge', 'chunks'),
      output: path.join(projectRoot, 'knowledge', 'knowledge-base.json')
    };

    this.fileManager = new FileManager(sourceDirs, targetDirs.raw);
    this.targetDirs = targetDirs;
    this.projectRoot = projectRoot;
  }

  /**
   * Phase 1: Collect files from cursor_docs and claude_docs
   */
  async phaseCollect() {
    console.log('\n' + '═'.repeat(60));
    console.log('KNOWLEDGE BASE PIPELINE - Phase 1: Collection');
    console.log('═'.repeat(60));

    const files = await this.fileManager.collectFiles();
    return files;
  }

  /**
   * Phase 2: Copy files to knowledge/raw
   */
  async phaseCopyToRaw() {
    console.log('\n' + '═'.repeat(60));
    console.log('KNOWLEDGE BASE PIPELINE - Phase 2: Copy to Raw');
    console.log('═'.repeat(60));

    const copiedFiles = await this.fileManager.copyAllFiles();
    return copiedFiles;
  }

  /**
   * Phase 3: Clean markdown files
   */
  async phaseClean(files) {
    console.log('\n' + '═'.repeat(60));
    console.log('KNOWLEDGE BASE PIPELINE - Phase 3: Clean Markdown');
    console.log('═'.repeat(60));

    const cleanedFiles = [];

    for (const file of files) {
      try {
        console.log(`\n🧹 Cleaning: ${file.fileName}`);

        // Read raw file
        const rawContent = await this.fileManager.readFile(file.targetPath);

        // Clean content
        const cleanedContent = this.cleaner.clean(rawContent);
        const stats = this.cleaner.getStats(rawContent, cleanedContent);

        console.log(`   Size: ${stats.originalLength} → ${stats.cleanedLength} bytes`);
        console.log(`   Lines: ${stats.originalLines} → ${stats.cleanedLines}`);
        if (stats.reducePercentage > 0) {
          console.log(`   Reduced by: ${stats.reducePercentage}%`);
        }

        // Write cleaned file
        const cleanedPath = path.join(this.targetDirs.cleaned, file.fileName);
        await this.fileManager.writeFile(cleanedPath, cleanedContent);
        console.log(`   ✓ Saved to knowledge/cleaned`);

        cleanedFiles.push({
          ...file,
          cleanedPath,
          cleanedContent,
          stats
        });
      } catch (error) {
        console.error(`   ✗ Error cleaning ${file.fileName}:`, error.message);
      }
    }

    console.log(`\n✅ Cleaned ${cleanedFiles.length}/${files.length} files`);
    return cleanedFiles;
  }

  /**
   * Phase 4: Sanitize for RAG
   */
  async phaseSanitize(files) {
    console.log('\n' + '═'.repeat(60));
    console.log('KNOWLEDGE BASE PIPELINE - Phase 4: Sanitize for RAG');
    console.log('═'.repeat(60));

    const sanitizedFiles = [];

    for (const file of files) {
      try {
        console.log(`\n🔍 Sanitizing: ${file.fileName}`);

        // Sanitize content
        const sanitizedContent = this.sanitizer.sanitize(file.cleanedContent);
        const stats = this.sanitizer.getStats(file.cleanedContent, sanitizedContent);

        console.log(`   Content: ${stats.originalLength} → ${stats.sanitizedLength} bytes`);
        if (stats.reducePercentage > 0) {
          console.log(`   Removed: ${stats.removePercentage}% (${stats.removedLength} bytes)`);
        }

        sanitizedFiles.push({
          ...file,
          sanitizedContent,
          stats
        });
      } catch (error) {
        console.error(`   ✗ Error sanitizing ${file.fileName}:`, error.message);
      }
    }

    console.log(`\n✅ Sanitized ${sanitizedFiles.length}/${files.length} files`);
    return sanitizedFiles;
  }

  /**
   * Phase 5: Split into chunks
   */
  async phaseChunk(files) {
    console.log('\n' + '═'.repeat(60));
    console.log('KNOWLEDGE BASE PIPELINE - Phase 5: Smart Chunking');
    console.log('═'.repeat(60));

    const allChunks = [];
    let totalChunks = 0;

    for (const file of files) {
      try {
        console.log(`\n📄 Chunking: ${file.fileName}`);

        // Split content into chunks
        const chunks = this.chunker.chunk(file.sanitizedContent, file.fileName);
        const stats = this.chunker.getStats(chunks);

        console.log(`   Total chunks: ${stats.totalChunks}`);
        console.log(`   Word counts: ${stats.minWords} - ${stats.maxWords} words`);
        console.log(`   Average: ${stats.averageWords} words/chunk`);
        console.log(`   In range: ${stats.chunksInRange}/${stats.totalChunks}`);

        allChunks.push({
          ...file,
          chunks,
          stats
        });

        totalChunks += chunks.length;
      } catch (error) {
        console.error(`   ✗ Error chunking ${file.fileName}:`, error.message);
      }
    }

    console.log(`\n✅ Created ${totalChunks} total chunks from ${files.length} files`);
    return allChunks;
  }

  /**
   * Phase 6: Add metadata and enrich chunks
   */
  async phaseMetadata(filesWithChunks) {
    console.log('\n' + '═'.repeat(60));
    console.log('KNOWLEDGE BASE PIPELINE - Phase 6: Enrich Metadata');
    console.log('═'.repeat(60));

    const enrichedChunks = [];

    for (const file of filesWithChunks) {
      console.log(`\n📋 Enriching: ${file.fileName}`);

      for (const chunk of file.chunks) {
        try {
          // Enrich chunk with metadata
          const enriched = this.metadata.enrich(chunk, {
            fileName: file.fileName,
            source: file.source
          });

          // Extract topics
          enriched.topics = this.metadata.extractTopics(chunk.content);

          // Validate metadata
          const validation = this.metadata.validate(enriched);
          if (!validation.isValid) {
            console.warn(`   ⚠ Validation issues:`, validation.issues.join(', '));
          }

          enrichedChunks.push(enriched);
        } catch (error) {
          console.error(`   ✗ Error enriching chunk:`, error.message);
        }
      }
    }

    // Generate summary
    const summary = this.metadata.generateSummary(enrichedChunks);
    console.log(`\n📊 Summary:`);
    console.log(`   Total chunks: ${summary.totalChunks}`);
    console.log(`   By type:`, JSON.stringify(summary.byType, null, 2));
    console.log(`   By source:`, JSON.stringify(summary.bySource, null, 2));
    console.log(`   By file:`, JSON.stringify(summary.byFile, null, 2));
    console.log(`   Date range: ${summary.dateRange.earliest} to ${summary.dateRange.latest}`);
    console.log(`   Total words: ${summary.totalWords}`);

    return {
      chunks: enrichedChunks,
      summary
    };
  }

  /**
   * Phase 7: Save chunks as files
   */
  async phaseSaveChunks(enrichedData) {
    console.log('\n' + '═'.repeat(60));
    console.log('KNOWLEDGE BASE PIPELINE - Phase 7: Save Chunks');
    console.log('═'.repeat(60));

    const chunks = enrichedData.chunks;
    let savedCount = 0;

    for (const chunk of chunks) {
      try {
        // Create filename based on source and ID
        const fileName = `${chunk.id}.md`;
        const filePath = path.join(this.targetDirs.chunks, fileName);

        // Create markdown content with metadata
        const markdown = this.createChunkMarkdown(chunk);

        // Write file
        await this.fileManager.writeFile(filePath, markdown);
        savedCount++;
      } catch (error) {
        console.error(`✗ Error saving chunk ${chunk.id}:`, error.message);
      }
    }

    console.log(`\n✅ Saved ${savedCount}/${chunks.length} chunks to knowledge/chunks`);
    return chunks;
  }

  /**
   * Create markdown representation of chunk
   * @param {Object} chunk - Chunk object with metadata
   * @returns {string} Markdown content
   */
  createChunkMarkdown(chunk) {
    let markdown = '';

    markdown += `# ${chunk.title || chunk.fileName}\n\n`;

    markdown += `## Metadata\n\n`;
    markdown += `- **ID**: ${chunk.id}\n`;
    markdown += `- **Type**: ${chunk.type}\n`;
    markdown += `- **Source**: ${chunk.source}\n`;
    markdown += `- **Date**: ${chunk.date}\n`;
    markdown += `- **File**: ${chunk.fileName}\n`;
    markdown += `- **Chunk**: ${chunk.chunkIndex + 1}/${chunk.chunkCount}\n`;
    markdown += `- **Words**: ${chunk.wordCount}\n`;

    if (chunk.topics && chunk.topics.length > 0) {
      markdown += `- **Topics**: ${chunk.topics.join(', ')}\n`;
    }

    markdown += `\n## Content\n\n`;
    markdown += chunk.content;

    return markdown;
  }

  /**
   * Phase 8: Generate knowledge-base.json
   */
  async phaseGenerateJSON(enrichedData) {
    console.log('\n' + '═'.repeat(60));
    console.log('KNOWLEDGE BASE PIPELINE - Phase 8: Generate JSON');
    console.log('═'.repeat(60));

    try {
      const output = {
        version: '1.0',
        generated: new Date().toISOString(),
        summary: enrichedData.summary,
        chunks: enrichedData.chunks
      };

      // Write JSON file
      const jsonContent = JSON.stringify(output, null, 2);
      await this.fileManager.writeFile(this.targetDirs.output, jsonContent);

      console.log(`\n✅ Generated knowledge-base.json`);
      console.log(`   Location: knowledge/knowledge-base.json`);
      console.log(`   Chunks: ${output.chunks.length}`);
      console.log(`   Size: ${(jsonContent.length / 1024).toFixed(2)} KB`);

      return output;
    } catch (error) {
      console.error('\n✗ Error generating JSON:', error.message);
      throw error;
    }
  }

  /**
   * Run complete pipeline
   */
  async run() {
    console.log('\n' + '═'.repeat(60));
    console.log('🚀 KNOWLEDGE BASE PIPELINE STARTED');
    console.log('═'.repeat(60));
    console.log(`Timestamp: ${new Date().toISOString()}`);

    const startTime = Date.now();

    try {
      // Initialize
      await this.initialize();

      // Phase 1: Collect
      const collectedFiles = await this.phaseCollect();

      // Phase 2: Copy to raw
      const copiedFiles = await this.phaseCopyToRaw();

      // Phase 3: Clean
      const cleanedFiles = await this.phaseClean(copiedFiles);

      // Phase 4: Sanitize
      const sanitizedFiles = await this.phaseSanitize(cleanedFiles);

      // Phase 5: Chunk
      const chunkedFiles = await this.phaseChunk(sanitizedFiles);

      // Phase 6: Metadata
      const enrichedData = await this.phaseMetadata(chunkedFiles);

      // Phase 7: Save chunks
      await this.phaseSaveChunks(enrichedData);

      // Phase 8: Generate JSON
      const finalOutput = await this.phaseGenerateJSON(enrichedData);

      // Summary
      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      console.log('\n' + '═'.repeat(60));
      console.log('✅ KNOWLEDGE BASE PIPELINE COMPLETED');
      console.log('═'.repeat(60));
      console.log(`Duration: ${duration}s`);
      console.log(`Output: ${this.targetDirs.output}`);
      console.log(`Chunks created: ${finalOutput.chunks.length}`);
      console.log('\nYour knowledge base is ready for RAG embeddings! 🎉');
      console.log('═'.repeat(60));

      return finalOutput;
    } catch (error) {
      console.error('\n' + '═'.repeat(60));
      console.error('❌ PIPELINE FAILED');
      console.error('═'.repeat(60));
      console.error('Error:', error.message);
      console.error(error.stack);
      process.exit(1);
    }
  }
}

// Main execution
if (require.main === module) {
  const pipeline = new KnowledgeBasePipeline();
  pipeline.run().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = KnowledgeBasePipeline;
