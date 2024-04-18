export { state_types as StateTypes, GetAppState, SetAppState } from './states';
export namespace MainIntf {
	export namespace cb {
		export type simple = () => void;
		export type base = (err:any, res?:any) => void;
		export type bool = (suc:boolean) => void;
	}
	export namespace api {
		
	}
}