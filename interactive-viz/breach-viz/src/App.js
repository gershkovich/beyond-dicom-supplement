import './App.css';
import BreachLocationTrends from './components/BreachLocationTrends';

function App() {
  return (
    <div className="App">
      <header className="App-header" style={{ backgroundColor: '#282c34', padding: '1rem', marginBottom: '2rem' }}>
        <h1 style={{ color: 'white', margin: 0 }}>Beyond DICOM Supplement: Interactive Visualization</h1>
        <p style={{ color: 'white', margin: '0.5rem 0 0' }}>
          Supplement to "Wearing a Fur Coat in the Summertime: Should Digital Pathology Redefine Medical Imaging?"
        </p>
      </header>
      
      <main style={{ padding: '0 1rem' }}>
        <BreachLocationTrends />
      </main>
      
      <footer style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f5f5f5', textAlign: 'center' }}>
        <p>© 2025 - Data source: <a href="https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf" target="_blank" rel="noopener noreferrer">HHS OCR Breach Portal</a></p>
      </footer>
    </div>
  );
}

export default App;
