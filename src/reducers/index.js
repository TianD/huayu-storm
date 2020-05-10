import { combineReducers } from 'redux';
import { project_list, get_project_list_failed, get_project_list_loading } from './project_list';
import { shot_list, get_shot_list_failed, get_shot_list_loading } from './shot_list';
import { overview_project_filters, overview_shot_filters } from './overview';
import { mayabatch_filters, mayabatch_items } from './mayabatch';
import { nukebatch_project_filters, nukebatch_shot_filters, nukebatch_taskid, nukebatch_items } from './nukebatch';
import { seq2movbatch_filters, seq2movbatch_items } from './seq2movbatch';

const rootReducer = combineReducers({
    project_list,
    get_project_list_failed,
    get_project_list_loading,
    shot_list,
    get_shot_list_failed,
    get_shot_list_loading,
    overview_project_filters,
    overview_shot_filters,
    mayabatch_filters,
    mayabatch_items,
    nukebatch_project_filters,
    nukebatch_shot_filters,
    nukebatch_taskid,
    nukebatch_items,
    seq2movbatch_filters,
    seq2movbatch_items
});

export default rootReducer;
