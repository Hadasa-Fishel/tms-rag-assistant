
const fs = require('fs').promises;
const path = require('path');

class FileManager {
  constructor(sourceDirs, targetDir) {
    this.sourceDirs = sourceDirs;
    this.targetDir = targetDir;
    this.collectedFiles = [];
  }

  /**
   * Recursively scan directories for .md files
   * @param {string} dir - Directory to scan
   * @param {string} sourceLabel - Label for source (cursor/claude)
   * @returns {Promise<Array>} Array of file objects with path and source
   */
  async scanDirectory(dir, sourceLabel) {
    const files = [];
    
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory()) {
          // Recursively scan subdirectories
          const subFiles = await this.scanDirectory(fullPath, sourceLabel);
          files.push(...subFiles);
        } else if (entry.isFile() && entry.name.endsWith('.md')) {
          files.push({
            fullPath,
            fileName: entry.name,
            source: sourceLabel,
            relativePath: path.relative(process.cwd(), fullPath)
          });
        }
      }
    } catch (error) {
      console.error(`Error scanning directory ${dir}:`, error.message);
    }
    
    return files;
  }

  /**
   * Collect all markdown files from source directories
   * @returns {Promise<Object>} Summary of collected files
   */
  async collectFiles() {
    console.log('\n📂 Phase 1: Collecting Markdown Files');
    console.log('─'.repeat(50));
    
    for (const [sourceDir, label] of Object.entries(this.sourceDirs)) {
      console.log(`\n🔍 Scanning: ${sourceDir} (${label})`);
      const files = await this.scanDirectory(sourceDir, label);
      
      if (files.length > 0) {
        console.log(`   ✓ Found ${files.length} file(s)`);
        files.forEach(file => {
          console.log(`     • ${file.fileName} [${file.source}]`);
        });
      }
      
      this.collectedFiles.push(...files);
    }
    
    console.log(`\n✅ Total files collected: ${this.collectedFiles.length}`);
    return this.collectedFiles;
  }

  /**
   * Copy file to target directory
   * @param {Object} file - File object
   * @returns {Promise<string>} Target file path
   */
  async copyFile(file) {
    try {
      const content = await fs.readFile(file.fullPath, 'utf-8');
      const targetPath = path.join(this.targetDir, file.fileName);
      
      await fs.writeFile(targetPath, content, 'utf-8');
      return targetPath;
    } catch (error) {
      console.error(`Error copying file ${file.fileName}:`, error.message);
      throw error;
    }
  }

  /**
   * Copy all collected files to target directory
   * @returns {Promise<Array>} Array of copied file paths
   */
  async copyAllFiles() {
    console.log('\n📋 Copying files to knowledge/raw...');
    console.log('─'.repeat(50));
    
    const copiedFiles = [];
    
    for (const file of this.collectedFiles) {
      try {
        const targetPath = await this.copyFile(file);
        console.log(`✓ Copied: ${file.fileName}`);
        copiedFiles.push({
          ...file,
          targetPath
        });
      } catch (error) {
        console.error(`✗ Failed to copy ${file.fileName}`);
      }
    }
    
    console.log(`\n✅ Successfully copied ${copiedFiles.length}/${this.collectedFiles.length} files`);
    return copiedFiles;
  }

  /**
   * Read file content
   * @param {string} filePath - Path to file
   * @returns {Promise<string>} File content
   */
  async readFile(filePath) {
    try {
      return await fs.readFile(filePath, 'utf-8');
    } catch (error) {
      console.error(`Error reading file ${filePath}:`, error.message);
      throw error;
    }
  }

  /**
   * Write file content
   * @param {string} filePath - Path to file
   * @param {string} content - Content to write
   * @returns {Promise<void>}
   */
  async writeFile(filePath, content) {
    try {
      await fs.writeFile(filePath, content, 'utf-8');
    } catch (error) {
      console.error(`Error writing file ${filePath}:`, error.message);
      throw error;
    }
  }

  /**
   * List all files in a directory
   * @param {string} dir - Directory path
   * @returns {Promise<Array>} Array of file paths
   */
  async listFiles(dir) {
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      return entries
        .filter(entry => entry.isFile())
        .map(entry => path.join(dir, entry.name));
    } catch (error) {
      console.error(`Error listing files in ${dir}:`, error.message);
      return [];
    }
  }
}

module.exports = FileManager;
