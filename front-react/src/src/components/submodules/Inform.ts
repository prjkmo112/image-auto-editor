import { Location } from 'react-router-dom';

import api from 'api';


class Inform {
  private static instance: Inform;

  private constructor() {
    
  }

  public static getInstance():Inform {
    if (!Inform.instance)
      Inform.instance = new Inform();

    return Inform.instance;
  }

  getUrlInfo(loc:Location<any>) {
    if (loc.pathname === "/") {
      return {
        title: { ko: "이미지 관리 툴", en: "Image Mangement Tool" },
      }
    } else {
      let loc_key = loc.pathname.replace(/^\//, '');
      let menu_item = api.menu.menu_list.find((v) => v.key === loc_key)

      return {
        title: { ko: menu_item?.krname, en: menu_item?.enname }
      }
    }
  }
}

const inform = Inform.getInstance();

export default inform;