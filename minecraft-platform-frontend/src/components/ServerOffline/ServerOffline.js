import AddServerForm from "./AddServerForm";
import MoneyPotSummary from "./MoneyPotSummary";
import RootDiv from '../../UI/RootDiv'

function ServerOffline(){
    return (
        <RootDiv>
            <AddServerForm/>
            <br></br>
            <br></br>
            <MoneyPotSummary/>
        </RootDiv>
    )
}

export default ServerOffline;
