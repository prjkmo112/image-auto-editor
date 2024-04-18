import { BrowserRouter, Routes, Route, useNavigate, useParams, useLocation } from 'react-router-dom';

import { SetAppState, StateTypes } from 'types';
import ContainBarLayout from 'views/layout/ContainBar';
import Home from 'views/home/Home';
import ClearedImg from 'views/clearedimg/ClearedImg';
import ExceptImg from 'views/exceptimg/ExceptImg';
import Err1 from 'views/error/404';


interface RouteListProps {
	setAppState: SetAppState;
}

const RoutesList = (props:RouteListProps) => {
	let navigate = useNavigate();
	let params = useParams();
	let location = useLocation();
	
	return (
		<Routes>
			<Route element={<ContainBarLayout navigate={navigate} params={params} location={location} />}>
				<Route index path='/' element={<Home />} />
				<Route path='/cleared_img' element={<ClearedImg setAppState={props.setAppState} />} />
				<Route path='/except_img' element={<ExceptImg />} />
			</Route>
			
			<Route path='*' element={<Err1 />} />
		</Routes>
	)
}

const RouteDump = (props:StateTypes.RouteDumpProps) => {
	return (
		<BrowserRouter>
			<RoutesList setAppState={props.setAppState} />
		</BrowserRouter>
	)
}

export default RouteDump;