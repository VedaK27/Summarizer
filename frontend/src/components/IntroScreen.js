import React from 'react';
import './IntroScreen.css';

export default function IntroScreen() {
  return (
    <div className="intro-container">
      {/* Animated background gradients */}
      <div className="bg-decoration bg-decoration-1"></div>
      <div className="bg-decoration bg-decoration-2"></div>
      <div className="bg-decoration bg-decoration-3"></div>

      <div className="intro-content">
        {/* Logo Section */}
        <div className="logo-section">
          
          <h1 className="logo-title">LazyWatch</h1>
          <p className="logo-subtitle">Intelligent Content Transformation</p>
        </div>

        {/* Main Content */}
        <div className="text-container">
          <p className="intro-text">
            In today's digital world, information is everywhere. Long videos,
            lengthy lectures, endless tutorials, meetings, podcasts, and articles
            demand hours of attention just to extract a few meaningful ideas.
            People often find themselves skipping, fast-forwarding, or abandoning
            content altogether because consuming everything fully is simply too
            time-consuming.
          </p>

          <p className="intro-text">
            This website is built for those moments — when you want the knowledge,
            not the effort. Our goal is to simplify the way you consume information
            by intelligently analyzing long-form content and transforming it into
            clear, concise, and structured insights. Instead of watching an entire
            video or reading pages of text, you get only what truly matters — the
            core ideas, important points, and a clear understanding of the topic.
          </p>

          <p className="intro-text">
            This helps you save time, stay focused, and learn more efficiently
            without feeling overwhelmed. Whether you are a student, a professional,
            or simply someone trying to make better use of your time, this website
            helps you absorb information faster and smarter, without losing meaning
            or context.
          </p>
        </div>

        {/* Highlighted Summary */}
        <div className="summary-box">
          <div className="summary-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <p className="intro-summary">
            No need to read long texts like this anymore!!
            Too long? Didn’t watch? Didn’t read? Relax — from now on, no more long texts or videos. We’ve got you covered.
          </p>
        </div>

        {/* Features Pills */}
        <div className="features-pills">
          <span className="pill">AI-Powered</span>
          <span className="pill">Time-Saving</span>
          <span className="pill">Instant Results</span>
        </div>
      </div>
    </div>
  );
}