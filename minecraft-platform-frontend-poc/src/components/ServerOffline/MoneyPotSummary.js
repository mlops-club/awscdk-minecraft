import './MoneyPotSummary.css';
import MoneyPotItem from "./MoneyPotItem";

function MoneyPotSummary(){

    let test_pot = {
        PotName:"Generic Pot",
        PotOwner:"Bill Sidine",
        AmountInPot:"$3.78"
    }

    return (
        <ul id="MoneyPotSummaryCard">
            <MoneyPotItem PotName={test_pot.PotName} PotOwner={test_pot.PotOwner} AmountInPot={test_pot.AmountInPot} />
        </ul>
    )
}

export default MoneyPotSummary;
