import './ServerStatus.css';
import PinkCard from '../../UI/PinkCard';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';

function createData(serverIP, serverPassword, remainingTime, playersOnline, availableRefund, fundingPotName, remainingFunds) {
  return { serverIP, serverPassword, remainingTime, playersOnline, availableRefund, fundingPotName, remainingFunds };
}

const rows = [
  createData('Frozen yoghurt', 159, 6.0, ["sdsdf"], 4.0, 3, 3)
];

export default function ServerStatus() {
  return (

    <PinkCard SectionHeader="Running Server Status">
    <TableContainer component={Paper} >
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>Server IP</TableCell>
            <TableCell align="right">Server Password</TableCell>
            <TableCell align="right">Remaining Time</TableCell>
            <TableCell align="right">Players Online</TableCell>
            <TableCell align="right">Available Refund For Terminating</TableCell>
            <TableCell align="right">Funding Pot Name</TableCell>
            <TableCell align="right">Remaining Funds In Pot</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow
              key={row.serverIP}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                {row.serverIP}
              </TableCell>
              <TableCell align="right">{row.serverPassword}</TableCell>
              <TableCell align="right">{row.remainingTime}</TableCell>
              <TableCell align="right">
                    <Tooltip title={row.playersOnline.join(',')}>
                    <strong><italic><a>
                      {row.playersOnline.length}
                    </a></italic></strong>
                  </Tooltip>
              </TableCell>
              <TableCell align="right">${row.availableRefund}</TableCell>
              <TableCell align="right">{row.fundingPotName}</TableCell>
              <TableCell align="right">${row.remainingFunds}</TableCell>
              <TableCell align="right"  ><Button variant="contained" color="error">Stop and Refund</Button></TableCell>
              <TableCell align="right"><Button variant="contained" color="success">Buy More Time</Button></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
        </PinkCard>
  );
}