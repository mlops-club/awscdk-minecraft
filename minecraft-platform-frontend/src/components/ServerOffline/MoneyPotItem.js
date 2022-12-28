import './MoneyPotItem.css';
import Card from '../../UI/Card';
import Button from '@mui/material/Button';
import BasicModal from '../../UI/Modal';

function MoneyPotItem(props){

    let modelOpenButton = <Button variant="contained" style={{"background-color":"darkolivegreen"}}>Add Money To Pot</Button>;

    let modalContent = <div>Placeholder</div>

    return (
        <li>
            <Card className='pot-item'>

                <div className='pot-owner'>
                  <div className='pot-owner__month'>Pot Owner</div>
                  <div className='pot-owner__day'>{props.PotOwner}</div>
                </div>

                <div className='pot-item__description'>
                    <h2>{props.PotName}</h2>
                    <BasicModal openButton={modelOpenButton}>{modalContent}</BasicModal>
                    <div className='pot-item__price'>{props.AmountInPot}</div>
              </div>
            </Card>

        </li>
    )
}

export default MoneyPotItem;
