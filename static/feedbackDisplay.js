import React, { useState, useEffect } from 'react';
import { ScrollText, Loader2 } from 'lucide-react';

const MuseumFeedbackDisplay = () => {
  const [feedbackEntries, setFeedbackEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const response = await fetch('/feedback'); // Flask endpoint for fetching feedback
        if (!response.ok) {
          throw new Error('Failed to fetch feedback');
        }
        const data = await response.json();
        setFeedbackEntries(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFeedback();
  }, []);

  if (isLoading) {
    return (
      <div className="loading-container">
        <Loader2 className="loader" />
        <p>Loading feedback...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        Error loading feedback: {error}
      </div>
    );
  }

  return (
    <div className="feedback-container">
      <h3 className="feedback-title">Visitor's Book</h3>
      {feedbackEntries.length === 0 ? (
        <p>No visitor entries yet.</p>
      ) : (
        feedbackEntries.map((entry) => (
          <div key={entry.id} className="feedback-entry">
            <p className="feedback-text">"{entry.feedback_text}"</p>
            <span className="feedback-name">— {entry.visitor_name || 'Anonymous Visitor'}</span>
            <span className="feedback-date">{new Date(entry.visit_date).toLocaleDateString()}</span>
          </div>
        ))
      )}
    </div>
  );
};

export default MuseumFeedbackDisplay;
