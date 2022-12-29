import React, { useState, useEffect, useReducer } from 'react';
import ServerOnline from '../components/ServerOnline/ServerOnline';
import ServerOffline from '../components/ServerOffline/ServerOffline';
import ServerProvisioning from "../components/ServerProvisioning/ServerProvisioning";
import ServerDeprovisioning from "../components/ServerProvisioning/ServerDeprovisioning";
import Login from '../components/Login/Login'
import AddUser from '../components/AddUser/AddUser';

const CurrentPageContext = React.createContext({
  currentPage: "server_offline",
  pageInformation:{}
});

function pageStateReducer(state, action){

  localStorage.setItem('currentPage', action.pageName);

  if (action.pageName === 'serverProvisioning'){
      if (action.hasOwnProperty("completedSteps")){
        state.pageStateData.serverProvisioning.completedSteps = action.completedSteps;
      }
      // state.currentPage = <ServerProvisioning completedSteps={state.pageStateData.serverProvisioning.completedSteps}/>;
      state.currentPage = <ServerProvisioning completedSteps={state.pageStateData.serverProvisioning.completedSteps}/>;
  } else {
    state.currentPage = state.pageStateData[action.pageName].htmlToRender;
  }
  return state
}

export const CurrentPageContextProvider = (props) => {
  const [currentPageState, updateCurrentPageState] = useReducer(pageStateReducer, {
    currentPage: <div>placeholder</div>,
    pageStateData:{
    addUser:{pageName:'addUser'},
    login:{pageName:'login', htmlToRender:<Login/>},
    serverOffline:{pageName:'serverOffline', htmlToRender:<ServerOffline/>},
    serverOnline:{pageName:'serverOnline', htmlToRender:<ServerOnline/>},
    serverProvisioning:{pageName:'serverProvisioning', htmlToRender:<ServerProvisioning completedSteps={0}/> ,completedSteps:0 },
    serverDeprovisioning:{pageName:'serverDeprovisioning', htmlToRender:<ServerDeprovisioning completedSteps={0}/>, completedSteps:0}
  }
  });

  const launchServer = (configurations) => {
    let numberMinutesToRunServer = configurations.numberMinutesToRunServer;
    let useSpotInstance = configurations.useSpotInstance;
    let serverSize = configurations.serverSize;
    let potToUse = configurations.potToUse;
    alert("sdf");
    updateCurrentPageState({pageName:"serverProvisioning", completedSteps:0});
  };

  function changeCompletedProvisioningSteps(stepToChangeTo){
      updateCurrentPageState({pageName:"serverProvisioning", completedSteps:stepToChangeTo});
  }

  useEffect(() => {
    const storedUserLoggedInInformation = localStorage.getItem('currentPage');
    updateCurrentPageState({pageName:"serverOffline"});
    // updateCurrentPageState({pageName:"serverProvisioning", completedSteps:0});
  }, []);

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
        currentPageState:currentPageState,
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
