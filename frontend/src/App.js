import './App.css';
import Header from './components/Header';
import SearchQuery from './components/SearchQuery';
import SearchResults from './components/SearchResults';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

function App() {
    return (
        <Router>
            <div className="App">
                <Header />
                <Routes>
                    <Route path='/' element={ <SearchQuery /> } />
                    <Route path='/searchresults' element={ <SearchResults /> } />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
