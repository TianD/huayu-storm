import React, { Component } from 'react';
import { Cascader, List, Select } from 'antd';
import { connect } from 'react-redux';
import MyCard from './MyCard';
import DetailView from './DetailView';
import { set_overview_project_filters, set_overview_shot_filters } from '../actions/overview';
import { get_shot_list } from '../actions/get_shot_list';


function mapStateToProps(state) {
    return {
        project_list: state.project_list,
        get_project_list_failed: state.get_project_list_failed,
        get_project_list_loading: state.get_project_list_loading,
        shot_list: state.shot_list,
        get_shot_list_failed: state.get_shot_list_failed,
        get_shot_list_loading: state.get_shot_list_loading,
        overview_project_filters: state.overview_project_filters,
        overview_shot_filters: state.overview_shot_filters
    }
}

function mapDispatchToProps(dispatch) {
    return {
        get_shot_list: (data) => dispatch(get_shot_list(data)),
        set_overview_project_filters: (data) => dispatch(set_overview_project_filters(data)),
        set_overview_shot_filters: (data) => dispatch(set_overview_shot_filters(data))
    }
}

class Overview extends Component {
    constructor(props) {
        super(props)
        this.state = {
            visible: false,
            shots: [],
            current_shot: {}
        }
    }

    changeVisible = (flag) => {
        this.setState({
            visible: flag
        })
    }

    onCardClick(item) {
        this.setState({
            current_shot: item
        },
            this.changeVisible(true))
    }

    filterShots = (value) => {
        console.log(value)
        this.props.set_overview_shot_filters(value)
        let shot_list = this.props.shot_list
        let result;
        if (value.length > 0) {
            let episode = shot_list.filter((element) => {
                return element["value"] === value[0]
            })[0]
            if (value[0] === 'all') {
                result = episode["shots"]
            } else {
                let sequence = episode["children"].filter((element) => {
                    return element["value"] === value[1]
                })[0]
                result = sequence["shots"]
            }
        } else {
            result = [];
        }
        this.setState({
            shots: result
        })
    }

    change_project(value) {
        this.props.set_overview_project_filters(value)
        this.props.get_shot_list(value)
    }

    componentDidMount() {
        this.change_project(this.props.overview_project_filters)
        this.filterShots(this.props.overview_shot_filters)
    }

    render() {
        let { visible, shots, current_shot } = this.state;
        return (
            <div>
                <Select
                    options={this.props.project_list}
                    defaultValue={this.props.overview_project_filters}
                    onChange={(value) => this.change_project(value)}
                    style={{ margin: 12, width: 140 }}
                />
                <Cascader
                    defaultValue={this.props.overview_shot_filters}
                    // style={{ position: 'absolute', left: '30px' }}
                    options={this.props.shot_list}
                    onChange={(value) => this.filterShots(value)}
                    placeholder="Please select" />
                <div style={{ padding: '50px' }}>
                    <List
                        itemLayout={'horizontal'}
                        dataSource={shots}
                        grid={{ gutter: 36, lg: 4, md: 3, sm: 1, xs: 1 }}
                        renderItem={
                            item => (
                                <List.Item>
                                    <MyCard shot={item} onClick={(e) => this.onCardClick(item)} />
                                </List.Item>
                            )
                        }
                    >
                    </List>
                </div>
                <DetailView shot={current_shot} visible={visible} changeVisible={this.changeVisible} />
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(Overview);