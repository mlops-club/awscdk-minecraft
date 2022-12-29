import * as React from 'react';
import { useState, useContext, useEffect } from 'react';
import Box from '@mui/material/Box';
import './Main.css';
import Navbar from "./Navbar";
import ServerOnline from './ServerOnline/ServerOnline';
import ServerOffline from './ServerOffline/ServerOffline';
import ServerProvisioning from "./ServerProvisioning/ServerProvisioning";
import Login from './Login/Login'
import AddUser from './AddUser/AddUser';
import AuthContext from "../store/auth-context";
import CurrentPageContext from "../store/current-page-context";

const Main = (props) => {
  let server_offline = "Server Offline";
  let server_online = "Server Online";
  let server_provisioning = "Server Provisioning";
  let login = "Login";
  let add_user = "Add User";
  let provisioning_server = "provisioning_server";
  let deprovisioning_server = "de_provisioning_server"

  const [currentPage, setCurrentPage] = useState(<Login/>);
  const authCtx = useContext(AuthContext);
  const currentPageCtx = useContext(CurrentPageContext);

  useEffect(() => {
    if (authCtx.isLoggedIn){
      setCurrentPage(<ServerOffline/>);
    } else {
      setCurrentPage(<Login/>);
    }
  }, []);

  const changePage = (new_page) => {
    if (new_page === server_offline){
      setCurrentPage(<ServerOffline/>);
    } else if (new_page === server_online){
      setCurrentPage(<ServerOnline/>);
    } else if (new_page === server_provisioning){
      setCurrentPage(<ServerProvisioning provisioning_type={provisioning_server} />);
    } else if (new_page === "Server Deprovision"){
      setCurrentPage(<ServerProvisioning provisioning_type={deprovisioning_server} />);
    } else if (new_page === "Logout"){
      authCtx.onLogout()
    } else if (new_page === login){
      setCurrentPage(<Login/>)
    } else if (new_page === add_user){
      setCurrentPage(<AddUser/>)
    }
  };

  return (
    <Box sx={{ minWidth: 120 }}>
      <Navbar onPageChange={changePage} ></Navbar>
        <br></br>
        <br></br>
        {!authCtx.isLoggedIn && <Login></Login>}
        {authCtx.isLoggedIn && currentPageCtx.currentPageState.currentPage}
    </Box>
  );
}

export default Main
