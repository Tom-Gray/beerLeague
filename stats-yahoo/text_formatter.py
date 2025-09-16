#!/usr/bin/env python3
"""
Text Formatter for Yahoo Fantasy League Data

This module handles formatting extracted data into readable text files.
"""

import os
import logging
from typing import Dict, List
from datetime import datetime

class TextFormatter:
    """Format extracted data into text files."""
    
    def __init__(self, output_dir: str = "data"):
        """Initialize the formatter with output directory."""
        self.output_dir = output_dir
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def format_final_rankings(self, rankings_data: List[Dict]) -> str:
        """Format final rankings data into readable text format."""
        if not rankings_data:
            return "No rankings data available."
        
        # Group rankings by season
        seasons = {}
        for record in rankings_data:
            season = record['season']
            if season not in seasons:
                seasons[season] = []
            seasons[season].append(record)
        
        # Sort seasons in descending order (most recent first)
        sorted_seasons = sorted(seasons.keys(), reverse=True)
        
        output_lines = []
        output_lines.append("=" * 60)
        output_lines.append("YAHOO FANTASY LEAGUE - FINAL RANKINGS")
        output_lines.append("=" * 60)
        output_lines.append("")
        
        for season in sorted_seasons:
            season_data = seasons[season]
            # Sort by rank (ensure rank is an integer)
            season_data.sort(key=lambda x: int(x['rank']) if isinstance(x['rank'], (int, str)) else 0)
            
            output_lines.append(f"SEASON {season}")
            output_lines.append("-" * 40)
            
            for record in season_data:
                rank = record['rank']
                team_name = record['team_name']
                wins = record.get('wins', 0)
                losses = record.get('losses', 0)
                ties = record.get('ties', 0)
                draft_position = record.get('draft_position')
                
                # Format the line similar to the requested format
                # #1    Team Name    (W-L-T) (Draft X)
                rank_str = f"#{rank}"
                record_str = f"({wins}-{losses}-{ties})"
                draft_str = f"(Draft {draft_position})" if draft_position is not None else ""
                
                # Calculate spacing to align records
                # Target format: #1    Team Name    (W-L-T) (Draft X)
                rank_width = 6  # "#1    "
                name_width = 30  # Reduced to make room for draft position
                
                # Truncate team name if too long
                display_name = team_name[:name_width-1] if len(team_name) >= name_width else team_name
                
                # Combine record and draft position
                full_record_str = f"{record_str} {draft_str}".strip()
                
                line = f"{rank_str:<{rank_width}}{display_name:<{name_width}}{full_record_str}"
                output_lines.append(line)
            
            output_lines.append("")  # Empty line between seasons
        
        # Add footer with extraction info
        output_lines.append("-" * 60)
        output_lines.append(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"Total records: {len(rankings_data)}")
        output_lines.append(f"Seasons: {', '.join(sorted_seasons)}")
        
        return "\n".join(output_lines)
    
    def export_rankings_to_text(self, rankings_data: List[Dict], filename: str = "final_rankings.txt") -> bool:
        """Export final rankings to a text file."""
        try:
            self.logger.info(f"Formatting {len(rankings_data)} ranking records for text export...")
            
            # Format the data
            formatted_text = self.format_final_rankings(rankings_data)
            
            # Write to file
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            
            self.logger.info(f"Successfully exported rankings to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting rankings to text: {e}")
            return False
    
    def export_all_text_formats(self, rankings_data: List[Dict], highest_scores: List[Dict], lowest_scores: List[Dict]) -> bool:
        """Export all data types to text files."""
        try:
            self.logger.info("Starting text export for all data...")
            
            success_count = 0
            total_exports = 1  # Only rankings for now
            
            # Export rankings
            if rankings_data:
                if self.export_rankings_to_text(rankings_data):
                    success_count += 1
            else:
                self.logger.warning("No rankings data to export")
            
            # TODO: Add highest/lowest scores text formatting when implemented
            if highest_scores:
                self.logger.info("Highest scores text export not implemented yet")
            
            if lowest_scores:
                self.logger.info("Lowest scores text export not implemented yet")
            
            self.logger.info(f"Successfully exported {success_count}/{total_exports} text formats")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error during text export: {e}")
            return False
