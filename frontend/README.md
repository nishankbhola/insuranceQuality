# Insurance Quality Control Frontend

A modern React-based frontend for the Insurance Quality Control System that validates auto insurance quotes against MVR and DASH reports.

## Features

- **Drag & Drop File Upload**: Easy file upload with visual feedback
- **Real-time Validation**: Instant processing and validation of documents
- **Detailed Reporting**: Comprehensive validation reports with issue categorization
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional interface with intuitive navigation

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend server running on port 8000

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will open at `http://localhost:3000`

## Usage

1. **Upload Documents**: Drag and drop or click to select PDF files
   - MVR reports should contain "MVR" in the filename
   - DASH reports should contain "DASH" in the filename  
   - Insurance quotes should contain "QUOTE" in the filename

2. **Review Results**: The system will automatically:
   - Extract data from all documents
   - Compare information across documents
   - Identify discrepancies and missing information
   - Generate a detailed validation report

3. **Analyze Issues**: Review the validation report to see:
   - Critical issues (data mismatches, missing convictions)
   - Warnings (missing documents)
   - Information about extracted data

## File Requirements

- **Format**: PDF files only
- **Naming**: Files must contain specific keywords in their names:
  - MVR reports: Include "MVR" in filename
  - DASH reports: Include "DASH" in filename
  - Insurance quotes: Include "QUOTE" in filename

## Technology Stack

- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **React Dropzone**: Drag and drop file upload
- **Axios**: HTTP client for API calls

## Development

### Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App

### Project Structure

```
src/
├── components/
│   ├── FileUpload.js      # File upload component
│   ├── ValidationResults.js # Results display component
│   └── Header.js          # Application header
├── App.js                 # Main application component
├── index.js              # Application entry point
└── index.css             # Global styles
```

## API Integration

The frontend communicates with the backend API running on `http://localhost:8000`. The main endpoint is:

- `POST /upload`: Upload files for validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Insurance Quality Control System. 