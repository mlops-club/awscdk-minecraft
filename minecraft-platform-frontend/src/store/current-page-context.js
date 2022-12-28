import React, { useState, useEffect } from 'react';
import ServerOnline from '../components/ServerOnline/ServerOnline';
import ServerOffline from '../components/ServerOffline/ServerOffline';
import ServerProvisioning from "../components/ServerProvisioning/ServerProvisioning";
import Login from '../components/Login/Login'
import AddUser from '../components/AddUser/AddUser';

const CurrentPageContext = React.createContext({
  currentPage: "server_offline",
  pageInformation:{}
});

export const CurrentPageContextProvider = (props) => {
  const [currentPage, setCurrentPage] = useState(<div>placeholder</div>);

  let pageStateDictionary = {
    addUser:{pageName:'addUser'},
    login:{pageName:'login', htmlToRender:<Login/>},
    serverOffline:{pageName:'serverOffline', htmlToRender:<ServerOffline/>},
    serverOnline:{pageName:'serverOnline', htmlToRender:<ServerOnline/>},
    serverProvisioning:{pageName:'serverProvisioning', htmlToRender:<ServerProvisioning/> },
    serverDeprovisioning:{pageName:'serverDeprovisioning', htmlToRender:<ServerProvisioning/>}
  }

  function prepareCurrentPage(pageState){
    localStorage.setItem('currentPage', pageState.pageName);
    setCurrentPage(pageState.htmlToRender)
  }

  useEffect(() => {
    const storedUserLoggedInInformation = localStorage.getItem('currentPage');
    if (pageStateDictionary.hasOwnProperty(storedUserLoggedInInformation) && false){
      prepareCurrentPage(pageStateDictionary[storedUserLoggedInInformation]);
    } else {
      prepareCurrentPage(pageStateDictionary.serverOffline);
    }
  }, []);

  const launchServer = (configurations) => {
    let numberMinutesToRunServer = configurations.numberMinutesToRunServer;
    let useSpotInstance = configurations.useSpotInstance;
    let serverSize = configurations.serverSize;
    let potToUse = configurations.potToUse;
    prepareCurrentPage(pageStateDictionary.serverProvisioning);
  };

  const terminateServer = (serverToTerminate) => {
    alert('serverToTerminate');
    alert(serverToTerminate);
  };

  const addMoney = (moneyConfigurations) => {
    alert('moneyConfigurations');
    alert(moneyConfigurations);
  };

  const addUser = (moneyConfigurations) => {
    alert('moneyConfigurations');
    alert(moneyConfigurations);
  };

  return (
    <CurrentPageContext.Provider
      value={{
        currentPage: currentPage,
        onLaunchServer: launchServer,
        onTerminateServer: terminateServer,
        onAddMoney: addMoney,
        onAddUser: addUser
      }}
    >
      {props.children}
    </CurrentPageContext.Provider>
  );
};

export default CurrentPageContext;
