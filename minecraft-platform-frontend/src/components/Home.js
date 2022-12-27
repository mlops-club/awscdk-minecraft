import * as React from 'react';
import { useState } from 'react';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import './Home.css';
import Navbar from "./Navbar";
import ServerOnline from './ServerOnline/ServerOnline';
import ServerOffline from './ServerOffline/ServerOffline';
import ServerProvisioning from "./ServerProvisioning/ServerProvisioning";

const Home = () => {
  let server_offline = "Server Offline";
  let server_online = "Server Online";
  let server_provisioning = "Server Provisioning";

  const [currentPage, setCurrentPage] = useState(<ServerProvisioning/>);

  const changePage = (new_page) => {
    if (new_page === server_offline){
      setCurrentPage(<ServerOffline/>);
    } else if (new_page === server_online){
      setCurrentPage(<ServerOnline/>);
    } else if (new_page === server_provisioning){
      setCurrentPage(<ServerProvisioning/>);
    } else if (new_page === "Logout"){
      setCurrentPage(<div>Log Out</div>);
    }
  };

  return (
    <Box sx={{ minWidth: 120 }}>
      <Navbar onPageChange={changePage} ></Navbar>
      <br></br>
      <br></br>
      {currentPage}
    </Box>
  );
}

export default Home

