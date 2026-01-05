const API_BASE_URL = "http://localhost:8000";

const apiService = {
  /**
   * Sends a video file to the backend for summarization
   * @param {File} videoFile 
   */
  summarizeVideo: async (videoFile) => {
    const formData = new FormData();
    formData.append("video", videoFile);

    console.log("API Call: summarizeVideo with file", videoFile.name);

    try {
      const response = await fetch(`${API_BASE_URL}/summarize_video`, {
        method: "POST",
        body: formData,
      });
      console.log("API Response Status:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to process video");
      }

      return await response.json();
    } catch (error) {
      console.error("API Error (summarizeVideo):", error);
      throw error;
    }
  },

  /**
   * Searches for keywords in processed videos
   * @param {string} keyword 
   */
  searchKeywords: async (keyword) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/keyword_summarize?q=${encodeURIComponent(keyword)}`
      );

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      return await response.json();
    } catch (error) {
      console.error("API Error (searchKeywords):", error);
      throw error;
    }
  }
};

export default apiService;