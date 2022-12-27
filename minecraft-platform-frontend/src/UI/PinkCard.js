import './PinkCard.css'
import * as React from 'react';
import Card from './Card'

function PinkCard(props){
    const classes = 'PinkCard ' + props.className;
    return (
        <Card className={classes}>
            <div className="sectionHeader">
                <h1>{props.SectionHeader}</h1>
                {props.children}
            </div>

        </Card>
    )
}

export default PinkCard;
