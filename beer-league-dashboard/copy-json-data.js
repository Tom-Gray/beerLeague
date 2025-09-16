#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

class JSONDataCopier {
    constructor() {
        this.sourceDir = path.join(__dirname, '..', 'stats-sleeper', 'data');
        this.outputDir = path.join(__dirname, 'frontend', 'public', 'data');
        
        // JSON files to copy
        this.jsonFiles = [
            'standings.json',
            'matchups.json',
            'analytics.json',
            'teams.json',
            'weekly-results.json'
        ];
    }

    async copy() {
        console.log('📊 Copying JSON data for Beer League Dashboard...');
        
        // Ensure output directory exists
        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true });
        }

        try {
            let copiedFiles = 0;
            
            for (const filename of this.jsonFiles) {
                const sourcePath = path.join(this.sourceDir, filename);
                const destPath = path.join(this.outputDir, filename);
                
                if (fs.existsSync(sourcePath)) {
                    fs.copyFileSync(sourcePath, destPath);
                    console.log(`✅ Copied ${filename}`);
                    copiedFiles++;
                } else {
                    console.log(`⚠️  ${filename} not found in source directory`);
                }
            }

            if (copiedFiles === 0) {
                console.error('❌ No JSON files found to copy!');
                console.log('Make sure to run the stats-sleeper scripts first to generate JSON data.');
                process.exit(1);
            }

            console.log(`✅ Successfully copied ${copiedFiles} JSON files!`);

        } catch (error) {
            console.error('❌ Error copying JSON data:', error);
            process.exit(1);
        }
    }
}

// Run the copier
if (require.main === module) {
    const copier = new JSONDataCopier();
    copier.copy();
}

module.exports = JSONDataCopier;
