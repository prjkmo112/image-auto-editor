import React, { Component } from "react";
import { Backdrop, CircularProgress } from '@mui/material';
import { SnackbarProvider, enqueueSnackbar } from 'notistack';

import RouteDump from 'comp/RouteDump';
import { StateTypes, GetAppState, MainIntf } from 'types';
import './app.global.scss'


class App extends Component<StateTypes.AppProps, StateTypes.AppState> {
  constructor(props:StateTypes.AppProps) {
    super(props);
    this.state = {
      loading: false,
      isMobile: false,
      snackbarInfo: { show: false, type: "default", msg: "", autoHideDuration: 3000 }
    }
  }

  getAppState:GetAppState<keyof StateTypes.AppState> = (key) => {
    return this.state[key];
  }

  setAppState = (key:keyof StateTypes.AppState, state:any, __cb__?:MainIntf.cb.simple) => {
    type AppStatesAll = Pick<StateTypes.AppState, keyof StateTypes.AppState>;

    if (key === "snackbarInfo" && state.show) {
      this.setState({
        snackbarInfo: { show: true, type: state.type, msg: state.msg }
      }, () => {
        enqueueSnackbar({
          key: "snackbar_app_main",
          anchorOrigin: { horizontal: "center", vertical: "top" },
          autoHideDuration: state.autoHideDuration || 2000,
          disableWindowBlurListener: true,
          message: state.msg
        });
        if (!!__cb__)
          __cb__();
      })
    } else {
      this.setState({ [key]: state } as AppStatesAll, __cb__);
    }
  }

  closeSnackbar = (e:Event|React.SyntheticEvent, reason?:any) => {
    this.setState({ snackbarInfo: { show: false, autoHideDuration: 2000, type: "info", msg: "" } });
  }

  render(): React.ReactNode {
    return (
      <>
        <RouteDump setAppState={this.setAppState} />

        <div>
          {/* Alert 부분 */}
          <SnackbarProvider 
            key="snackbar_app_main" 
            maxSnack={4} 
            variant={this.state.snackbarInfo.type} 
            dense={this.state.isMobile} 
          />
        </div>

        {/* 로딩 */}
        <Backdrop
          sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
          open={this.state.loading}
          onClick={() => this.setState({ loading: false })}
        >
          <CircularProgress />
        </Backdrop>
      </>
    )
  }
}

export default App;