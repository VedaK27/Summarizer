import React, { useState, useRef } from "react";
import "./Home.css";
import logo from "../assets/logo.png";
import apiService from "../services/apiservice";

export default function Home() {
  const [activeTab, setActiveTab] = useState("upload");
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [results, setResults] = useState([]);
  const fileInputRef = useRef(null);



  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };
const handleProcess = async () => {
  if (!selectedFile) return;

  console.log("Processing file:", selectedFile.name);

  setIsProcessing(true);
  try {
    // Calling the service instead of writing fetch here
    console.log("Sending file to backend for summarization...");
    const data = await apiService.summarizeVideo(selectedFile);

    // Update state with backend data
    setResults({
      summary: data.summary.final_summary || "No summary generated",
      keyPoints: data.summary.key_points || [],
      mindmapFile: data.mindmap_file
    });

    setActiveTab("results");
  } catch (error) {
    alert(`Error: ${error.message}`);
  } finally {
    setIsProcessing(false);
  }
};

 const handleSearch = async () => {
  if (!searchKeyword.trim()) return;
  
  try {
    const searchData = await apiService.searchKeywords(searchKeyword);
    console.log("Search Results:", searchData);
    // Handle displaying search results here
  } catch (error) {
    console.error("Search failed:", error.message);
  }
};

  return (
    <div className="home-container">
      {/* Header */}
      <header className="home-header">
        <div className="header-content">
          <div className="logo-container">
            <img src={logo} alt="LazyWatch Logo" className="logo-image" />
            <div>
              <h2 className="logo-title">LazyWatch</h2>
              <p className="logo-subtitle">Intelligent Video Summarizer</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="home-main">
        {/* Tabs */}
        <nav className="tabs-container">
          <button
            className={`tab ${activeTab === "upload" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("upload")}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              className="tab-icon"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            Upload Video
          </button>
          <button
            className={`tab ${activeTab === "results" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("results")}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              className="tab-icon"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Results
          </button>
          <button
            className={`tab ${activeTab === "search" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("search")}
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              className="tab-icon"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            Keyword Search
          </button>
        </nav>

        {/* Upload Tab */}
        {activeTab === "upload" && (
          <div className="card">
            <h3 className="card-title">Upload Your Video</h3>
            <p className="card-subtitle">
              Select a video file to generate intelligent summaries
            </p>

            <div
              className={`upload-box ${
                isDragging ? "upload-box-dragging" : ""
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={handleUploadClick}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileSelect}
                className="file-input"
              />

              <div className="upload-icon-container">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  className="upload-icon"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>

              {selectedFile ? (
                <div className="file-selected">
                  <p className="file-name">{selectedFile.name}</p>
                  <p className="file-size">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <>
                  <p className="upload-title">
                    {isDragging
                      ? "Drop it here!"
                      : "Drop your video here or click to browse"}
                  </p>
                  <span className="upload-formats">
                    MP4, MOV, AVI, MKV • Max 500MB
                  </span>
                </>
              )}
            </div>

            {selectedFile && (
              <button
                className="process-button"
                onClick={handleProcess}
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <>
                    <div className="spinner"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      className="button-icon"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                    Generate Summary
                  </>
                )}
              </button>
            )}
          </div>
        )}

        {/* Results Tab */}
        {activeTab === "results" && (
          <div className="results-container">
            <div className="card">
              <h3 className="card-title">Summary</h3>
              <p className="summary-text">{results.summary}</p>
            </div>

            <div className="card">
              <h3 className="card-title">Key Points</h3>
              <ul className="key-points-list">
                {results.keyPoints.map((point, index) => (
                  <li key={index} className="key-point-item">
                    <span className="key-point-bullet">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Search Tab */}
        {activeTab === "search" && (
          <div className="card">
            <h3 className="card-title">Keyword Search</h3>
            <p className="card-subtitle">
              Search for specific topics within your processed videos
            </p>

            <div className="search-form">
              <div className="search-input-container">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  className="search-icon"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <input
                  type="text"
                  placeholder="Enter keywords to search..."
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  className="search-input"
                />
              </div>
              <button onClick={handleSearch} className="search-button">
                Search
              </button>
            </div>

            <div className="search-hint">
              <p className="hint-text">
                💡 Tip: Search for specific topics, names, or concepts mentioned
                in your videos
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      
    </div>
  );
}
