import React from 'react';

interface ExportButtonProps {
  exportUrl: string;
}

export const ExportButton: React.FC<ExportButtonProps> = ({ exportUrl }) => {
  return (
    <a href={exportUrl} download className="export-btn" title="Export filtered data to CSV">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 1v9M8 10L5 7M8 10l3-3M2 12v1.5A1.5 1.5 0 003.5 15h9a1.5 1.5 0 001.5-1.5V12"
          stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
      Export CSV
    </a>
  );
};
