import { MenuAPI } from "./submodules/menu"
import { GetImagesAPI } from './submodules/get_images'

const menu = MenuAPI.getInstance()
const getimg = GetImagesAPI.getInstance();

let __default = {
    menu, getimg
}
export default __default;