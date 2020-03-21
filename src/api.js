import axios from 'axios';

//todo export this to global const
axios.defaults.baseURL = 'http://127.0.0.1:5000/api'


class Api {

    get_project_list(callback) {
        axios.get('/get_project_list')
            .then(callback)
    }

    get_thumbnail_url(shot) {
        return axios.defaults.baseURL + "/get_thumbnail?preview=" + shot["preview"]
    }
}

const api = new Api()

export default api