import { Navigate, Outlet } from 'react-router'

function PrivateRoute() {
    const auth = true
    return (
        auth ? <Outlet /> : <Navigate to="login" />
    );
};

export default PrivateRoute