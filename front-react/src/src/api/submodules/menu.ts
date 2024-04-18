interface menu_list_item {
    krname: string;
    enname: string;
    key:    string;
}

export class MenuAPI {
    private static instance: MenuAPI;
    private _menu_list:        menu_list_item[];

    constructor() {
        this._menu_list = [
            { krname: "정리된 이미지", enname: "CLEARED IMAGES", key: "cleared_img" },
            { krname: "제외 설정된 이미지", enname: "EXCEPT IMAGES", key: "except_img" }
        ]
    }

    public static getInstance() {
        if (!MenuAPI.instance) {
            MenuAPI.instance = new MenuAPI();
        }
        return MenuAPI.instance;
    }

    public get menu_list() : menu_list_item[] {
        return this._menu_list;
    }
}