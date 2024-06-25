import Leaderboard from './assets/components/Leaderboard';
import './App.css';
import { LeaderboardEntry } from './assets/Types';
import { useEffect, useState } from 'react';

function App() {
  const [data, setData] = useState<LeaderboardEntry[]>([]);

  useEffect(() => {
    const apiUrl = "http://arcadepc:9090/highscores";

    fetch(`${apiUrl}/highscores`)
      .then(response => response.json())
      .then(data => {
        const formattedData: LeaderboardEntry[] = Object.entries(data).map(([key, val]: [string, any]) => ({
          Playername: key,
          Score: val.highscore,
        }));
        setData(formattedData);
      })
      .catch(error => console.error('Error fetching highscores:', error));
  }, []);

  return (
    <>
      <Leaderboard data={data} />
    </>
  );
}

export default App;
