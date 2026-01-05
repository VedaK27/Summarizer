import React, { useState, useRef } from "react";
import "./Home.css";
import logo from "../assets/logo.png";
import Mermaid from "./Mermaid";
import apiService from "../services/apiService";

export default function Home() {
  const [activeTab, setActiveTab] = useState("upload");
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [results, setResults] = useState([]);
  const [searchData, setSearchData] = useState(null); // Add state for keyword search results
  const [isSearching, setIsSearching] = useState(false); // Add searching state
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
    console.log("Sending file to backend for summarization...");
    const data = await apiService.summarizeVideo(selectedFile);

    // 1. Extract Summary
    const summaryText = data.summary?.overall_summary || "No summary generated";

    // 2. Extract Key Points
    const extractedKeyPoints = data.summary?.segments 
      ? data.summary.segments.flatMap(segment => segment.key_points || []) 
      : [];

    // 3. Extract Topic (New Step)
    const extractedTopic = data.summary?.segments?.[0]?.topic || "";

    // Update state with EVERYTHING (including the new topic)
    setResults({
      summary: summaryText,
      keyPoints: extractedKeyPoints,
      mindmapFile: data.mindmap_file,
      mindmapCode: data.mindmap_code, // Add this line
      topic: extractedTopic // <--- We save it here!
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
    
    setIsSearching(true);
    try {
      const data = await apiService.searchKeywords(searchKeyword);
      console.log("Search Results:", data);
      setSearchData(data); // Save the results
    } catch (error) {
      console.error("Search failed:", error.message);
      alert(`Search failed: ${error.message}`);
    } finally {
      setIsSearching(false);
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
              
              {/* Use results.topic here (NOT data) */}
              {results.topic && (
                 <h4 style={{marginBottom: '10px', color: '#666'}}>
                   Topic: {results.topic}
                 </h4>
              )}

              <p className="summary-text">{results.summary}</p>
            </div>
            {results.mindmapCode && (
              <div className="card">
                <h3 className="card-title">Mindmap</h3>
                <div className="mindmap-wrapper" style={{ padding: "20px", background: "#fff", borderRadius: "8px" }}>
                  <Mermaid chart={results.mindmapCode} />
                </div>
              </div>
            )}

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
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="search-input"
                />
              </div>
              <button 
                onClick={handleSearch} 
                className="search-button"
                disabled={isSearching}
              >
                {isSearching ? "Searching..." : "Search"}
              </button>
            </div>

            {searchData && (
              <div className="search-results" style={{ marginTop: "30px" }}>
                {searchData.error ? (
                  <div className="card" style={{ border: "1px solid #fee2e2", background: "#fef2f2" }}>
                    <p style={{ color: "#dc2626", margin: 0 }}>{searchData.error}</p>
                  </div>
                ) : (
                  <div className="card" style={{ border: "1px solid #e2e8f0" }}>
                    <h4 style={{ color: "#1e293b", marginBottom: "12px", borderBottom: "1px solid #f1f5f9", paddingBottom: "8px" }}>
                      Results for: "{searchData.topic || searchKeyword}"
                    </h4>
                    <p className="summary-text" style={{ fontSize: "0.95rem", color: "#475569" }}>
                      {searchData.summary}
                    </p>
                    {searchData.key_points && searchData.key_points.length > 0 && (
                      <div style={{ marginTop: "20px" }}>
                        <h5 style={{ fontSize: "0.9rem", color: "#1e293b", marginBottom: "10px" }}>Key Points:</h5>
                        <ul className="key-points-list">
                          {searchData.key_points.map((point, index) => (
                            <li key={index} className="key-point-item" style={{ padding: "8px 0", fontSize: "0.9rem" }}>
                              <span className="key-point-bullet">•</span>
                              {point}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

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
