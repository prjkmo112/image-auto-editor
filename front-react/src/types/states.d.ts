import { NavigateFunction, Params, Location } from "react-router-dom";

interface RRD_withnpl {
  navigate:   NavigateFunction;
  params:     Readonly<Params<string>>;
  location:   Location<any>;
}

interface SnackBarInfoType {
    show:               boolean;
    autoHideDuration?:  number;
    type:               "default" | "error" | "success" | "warning" | "info";
    msg:                string;
}

declare type SetAppState = (key:keyof state_types.AppState, state:any, __cb__?:MainIntf.cb.simple) => void;
declare type GetAppState<T extends keyof StateTypes.AppState> = (key: T) => StateTypes.AppState[T];

declare type SELRRD = "rrd"|"raw"|undefined;
declare type RRDTYPE<T extends SELRRD, U> = T extends "rrd" ? RRD_withnpl & U : U;

declare namespace state_types {
    // src/App.tsx
    export interface AppProps {}
    export interface AppState {
        loading:        boolean;
        isMobile:       boolean;
        snackbarInfo:   SnackBarInfoType;
    }

    // components/RouteDump.tsx
    export interface RouteDumpProps {
        setAppState:    SetAppState;
    }
    export interface RouteDumpState {}

    // views/layout/ContainerBar.tsx
    interface _ContainerBarProps {
    }
    export type ContainerBarProps<T> = RRDTYPE<T, _ContainerBarProps>;
    export interface ContainerBarState {
        openLeftbar:    boolean;
    }

    interface ClearedImgState_search_condition_item {
        label:      string;
        value:      string;
        include:    boolean;
        showchip?:  boolean;
    }
    interface ClearedImgState_result_item {
        label:              any;
        axis:               { yst: number, yend: number, distance: number }[]
        image:              string;
        origin_image:       string;
        drawed_orgin_image: string;
    }
    export interface ClearedImgProps {
        setAppState:    SetAppState;
    }
    export interface ClearedImgState {
        search_condition:       ClearedImgState_search_condition_item[];
        result:                 ClearedImgState_result_item[];
        selected_res:           ClearedImgState_result_item|null;
        detail_view_type_view:  string;
        detail_view_type_tool:  string[];
    }

    export interface ExceptImgProps {

    }
    export interface ExceptImgState {
        img_search_code:    string;
        content_loading:    boolean;
        img_list:           string[];
    }
}