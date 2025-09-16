#!/usr/bin/env python3
"""
CSV Export Module for Yahoo Fantasy Data

This module handles the export of extracted fantasy data to CSV format.
"""

import pandas as pd
import os
from pathlib import Path
from typing import List, Dict
import logging

class CSVExporter:
    """Export fantasy data to CSV files."""
    
    def __init__(self, output_dir: str = "data"):
        """Initialize the CSV exporter."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def export_final_rankings(self, rankings_data: List[Dict], filename: str = "final_rankings_by_season.csv"):
        """Export final rankings data to CSV."""
        try:
            if not rankings_data:
                self.logger.warning("No rankings data to export")
                return False
            
            # Create DataFrame
            df = pd.DataFrame(rankings_data)
            
            # Sort by season and rank
            df = df.sort_values(['season', 'rank'])
            
            # Reorder columns for better readability
            column_order = [
                'season', 'rank', 'team_name', 'wins', 'losses', 'ties',
                'points_for', 'points_against', 'team_key', 'extracted_date'
            ]
            
            # Only include columns that exist in the data
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            # Export to CSV
            output_path = self.output_dir / filename
            df.to_csv(output_path, index=False)
            
            self.logger.info(f"Exported {len(df)} ranking records to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting rankings data: {e}")
            return False
    
    def export_highest_scores(self, scores_data: List[Dict], filename: str = "highest_scores_by_season.csv"):
        """Export highest scores data to CSV."""
        try:
            if not scores_data:
                self.logger.warning("No highest scores data to export")
                return False
            
            # Create DataFrame
            df = pd.DataFrame(scores_data)
            
            # Sort by season and week
            df = df.sort_values(['season', 'week'])
            
            # Reorder columns for better readability
            column_order = [
                'season', 'week', 'team_name', 'points', 'team_key', 'extracted_date'
            ]
            
            # Only include columns that exist in the data
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            # Round points to 2 decimal places
            if 'points' in df.columns:
                df['points'] = df['points'].round(2)
            
            # Export to CSV
            output_path = self.output_dir / filename
            df.to_csv(output_path, index=False)
            
            self.logger.info(f"Exported {len(df)} highest score records to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting highest scores data: {e}")
            return False
    
    def export_lowest_scores(self, scores_data: List[Dict], filename: str = "lowest_scores_by_season.csv"):
        """Export lowest scores data to CSV."""
        try:
            if not scores_data:
                self.logger.warning("No lowest scores data to export")
                return False
            
            # Create DataFrame
            df = pd.DataFrame(scores_data)
            
            # Sort by season and week
            df = df.sort_values(['season', 'week'])
            
            # Reorder columns for better readability
            column_order = [
                'season', 'week', 'team_name', 'points', 'team_key', 'extracted_date'
            ]
            
            # Only include columns that exist in the data
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            # Round points to 2 decimal places
            if 'points' in df.columns:
                df['points'] = df['points'].round(2)
            
            # Export to CSV
            output_path = self.output_dir / filename
            df.to_csv(output_path, index=False)
            
            self.logger.info(f"Exported {len(df)} lowest score records to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting lowest scores data: {e}")
            return False
    
    def export_all_data(self, rankings_data: List[Dict], highest_scores_data: List[Dict], 
                       lowest_scores_data: List[Dict]) -> bool:
        """Export all data types to their respective CSV files."""
        try:
            self.logger.info("Starting CSV export for all data...")
            
            success_count = 0
            
            # Export rankings
            if self.export_final_rankings(rankings_data):
                success_count += 1
            
            # Export highest scores
            if self.export_highest_scores(highest_scores_data):
                success_count += 1
            
            # Export lowest scores
            if self.export_lowest_scores(lowest_scores_data):
                success_count += 1
            
            self.logger.info(f"Successfully exported {success_count}/3 data types")
            return success_count == 3
            
        except Exception as e:
            self.logger.error(f"Error during bulk export: {e}")
            return False
    
    def create_summary_report(self, rankings_data: List[Dict], highest_scores_data: List[Dict], 
                            lowest_scores_data: List[Dict], filename: str = "extraction_summary.csv"):
        """Create a summary report of the extracted data."""
        try:
            self.logger.info("Creating extraction summary report...")
            
            # Analyze the data
            seasons_in_rankings = set(item['season'] for item in rankings_data) if rankings_data else set()
            seasons_in_highest = set(item['season'] for item in highest_scores_data) if highest_scores_data else set()
            seasons_in_lowest = set(item['season'] for item in lowest_scores_data) if lowest_scores_data else set()
            
            all_seasons = seasons_in_rankings.union(seasons_in_highest).union(seasons_in_lowest)
            
            summary_data = []
            for season in sorted(all_seasons):
                rankings_count = len([item for item in rankings_data if item['season'] == season])
                highest_count = len([item for item in highest_scores_data if item['season'] == season])
                lowest_count = len([item for item in lowest_scores_data if item['season'] == season])
                
                summary_data.append({
                    'season': season,
                    'teams_in_rankings': rankings_count,
                    'highest_score_weeks': highest_count,
                    'lowest_score_weeks': lowest_count,
                    'data_complete': rankings_count > 0 and highest_count > 0 and lowest_count > 0
                })
            
            # Create DataFrame and export
            df = pd.DataFrame(summary_data)
            output_path = self.output_dir / filename
            df.to_csv(output_path, index=False)
            
            self.logger.info(f"Created summary report: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating summary report: {e}")
            return False
    
    def list_exported_files(self):
        """List all CSV files in the output directory."""
        try:
            csv_files = list(self.output_dir.glob("*.csv"))
            
            if csv_files:
                self.logger.info("Exported CSV files:")
                for file_path in sorted(csv_files):
                    file_size = file_path.stat().st_size
                    self.logger.info(f"  - {file_path.name} ({file_size:,} bytes)")
            else:
                self.logger.info("No CSV files found in output directory")
                
            return csv_files
            
        except Exception as e:
            self.logger.error(f"Error listing exported files: {e}")
            return []
