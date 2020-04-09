import { combineReducers } from 'redux';
import { project_list, get_project_list_failed, get_project_list_loading } from './project_list';
import overview_filters from './overview_filters';
import mayabatch_filters from './mayabatch_filters';
import nukebatch_filters from './nukebatch_filters';
import seq2mov_filters from './seq2mov_filters';
import show_detailview from './show_detailview';

const rootReducer = combineReducers({
    project_list,
    get_project_list_failed,
    get_project_list_loading
    // overview_filters,
    // mayabatch_filters,
    // nukebatch_filters,
    // seq2mov_filters,
    // show_detailview
});

export default rootReducer;
