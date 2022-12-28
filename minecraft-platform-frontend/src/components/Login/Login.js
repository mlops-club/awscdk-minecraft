import './Login.css';
import { useState } from 'react';
import RootDiv from '../../UI/RootDiv';
import PinkCard from '../../UI/PinkCard'
import SignIn from './LoginForm'

const Login = () => {
    return (
    <RootDiv>
        <PinkCard>
            <SignIn/>
        </PinkCard>
    </RootDiv>
    );
}

export default Login
