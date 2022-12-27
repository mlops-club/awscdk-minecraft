import './MoneyPotItem.css';
import Card from '../../UI/Card';

function MoneyPotItem(props){
    return (
        <li>
            <Card className='pot-item'>

                <div className='pot-owner'>
                  <div className='pot-owner__month'>Pot Owner</div>
                  <div className='pot-owner__day'>{props.PotOwner}</div>
                </div>

                <div className='pot-item__description'>
                    <h2>{props.PotName}</h2>
                <div className='pot-item__price'>{props.AmountInPot}</div>
              </div>
            </Card>

        </li>
    )
}

export default MoneyPotItem;
