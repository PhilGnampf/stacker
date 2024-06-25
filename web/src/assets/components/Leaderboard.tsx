import 'bulma/css/bulma.css';
import { LeaderboardEntry } from '../Types';

interface IProps {
    data: LeaderboardEntry[]
}

function Leaderboard({ data }: IProps) {
    return (
        <>
            <table className="table">
                <thead>
                    <tr>
                        <th><abbr title="Player">Player</abbr></th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
                    {
                        data.map((val, index) => (
                            <tr key={index}>
                                <td>{val.Playername}</td>
                                <td>{val.Score}</td>
                            </tr>
                        ))
                    }
                </tbody>
            </table>
        </>
    );
}

export default Leaderboard;
