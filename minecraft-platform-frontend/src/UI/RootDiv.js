import './RootDiv.css';

function RootDiv(props){
    const classes = 'ServerOfflineHeader ' + props.className;
    return <div className={classes}>{props.children}</div>;

}

export default RootDiv;
