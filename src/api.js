import axios from 'axios';

//todo export this to global const
axios.defaults.baseURL = 'http://127.0.0.1:5000/api'


class Api {

    get_project_list() {
        return axios.get('/get_project_list')
    }

    get_thumbnail_url(shot) {
        return axios.defaults.baseURL + "/get_thumbnail?preview=" + shot["preview"]
    }

    get_detail(shot) {
        return axios.post('/get_detail', shot)
    }

    nuke_setup_process(shot) {
        return axios.post('/nuke_setup_process', shot)
    }
}

const api = new Api()

export default api