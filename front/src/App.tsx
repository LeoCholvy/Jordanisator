import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './reset.css';
// import './App.css'
import Logger from './components/Logger';

// Composants de pages
const Home: React.FC = () => {
    return (
        <div>
            <h1>Accueil</h1>
            <p>Bienvenue sur la page d'accueil</p>
            <Logger />
        </div>
    );
};

const About: React.FC = () => {
    return (
        <div>
            <h1>À propos</h1>
            <p>Page à propos de notre application</p>
        </div>
    );
};

const Contact: React.FC = () => {
    return (
        <div>
            <h1>Contact</h1>
            <p>Contactez-nous ici</p>
        </div>
    );
};

// Composant de navigation
const Navigation: React.FC = () => {
    return (
        <nav style={{ padding: '20px', borderBottom: '1px solid #ccc' }}>
            <Link to="/" style={{ marginRight: '15px' }}>Accueil</Link>
            <Link to="/about" style={{ marginRight: '15px' }}>À propos</Link>
            <Link to="/contact">Contact</Link>
        </nav>
    );
};

const App: React.FC = () => {
    return (
        <Router>
            <div className="App">
                <Navigation />
                <main style={{ padding: '20px' }}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/about" element={<About />} />
                        <Route path="/contact" element={<Contact />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
};

export default App;