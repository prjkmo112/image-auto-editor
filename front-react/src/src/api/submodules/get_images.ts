import axios, { AxiosInstance } from 'axios';
import qs from 'qs';
import { MainIntf } from 'types';
import Utils from 'comp/Utils';


export class GetImagesAPI {
    private static instance: GetImagesAPI;
    private axios: AxiosInstance;

    constructor() {
        this.axios = axios.create({
            baseURL: `${process.env.FRONT_BACK_HOST}/settings`,
            timeout: 5000,
            headers: {
                'Access-Control-Allow-Origin': "*"
            }
        })
    }

    public static getInstance() {
        if (!GetImagesAPI.instance)
            GetImagesAPI.instance = new GetImagesAPI();

        return GetImagesAPI.instance;
    }

    excepted(code:string, include:boolean, __cb__:MainIntf.cb.base) {
        this.axios.get(`/get_ex_img?code=${code}&include=${include ? "True" : "False"}`).then((res) => {
            __cb__(null, res.data);
        }).catch((err) => {
            __cb__(err);
        })
    }

    cleared(filter:any, __cb__:MainIntf.cb.base) {
        let data = qs.stringify({
            "fil": filter
        });
        this.axios.post('/get_settedimg', {
            "fil": filter
        }).then((res) => {
            let data = res.data;
            __cb__(null, data);
        }).catch((err) => {
            __cb__(err);
        })
    }
}