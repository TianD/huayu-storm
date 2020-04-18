import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Table, Button, Select, Row, Col } from 'antd';
import { PlayCircleTwoTone, RestTwoTone } from '@ant-design/icons';
import {set_mayabatch_filters, set_mayabatch_items} from '../actions/mayabatch';
import api from '../api'

const {remote } = window.electron;

function mapStateToProps(state) {
    return {
        project_list: state.project_list,
        get_project_list_failed: state.get_project_list_failed,
        get_project_list_loading: state.get_project_list_loading,
        mayabatch_filters: state.mayabatch_filters,
        mayabatch_items: state.mayabatch_items
    }
}

function mapDispatchToProps(dispatch) {
    return {
        set_mayabatch_filters: (data)=>dispatch(set_mayabatch_filters(data)),
        set_mayabatch_items: (data)=>dispatch(set_mayabatch_items(data))
    }
}

class BatchTableForMaya extends Component {

    constructor(props) {
        super(props)
        this.columns = [
            {
                title: 'Id',
                dataIndex: 'id',
                key: 'id',
            },
            {
                title: '状态',
                dataIndex: 'status',
                key: 'status',
            },
            {
                title: '文件',
                dataIndex: 'name',
                key: 'Name',
            },
            {
                title: 'Action',
                dataIndex: 'action',
                key: 'action',
                render: (text, record) => (
                    <span>
                        <Button onClick={()=>{this.playThis(record)}} 
                        style={{ margin: 3 }} ghost shape="circle" icon={<PlayCircleTwoTone twoToneColor="#52c41a" />} />
                        <Button onClick={()=>{this.removeThis(record)}} 
                        style={{ margin: 3 }} ghost shape="circle" icon={<RestTwoTone twoToneColor="#eb2f96" />} />
                    </span>
                )
            }
        ]
    }

    async playThis(record, index) {
        let file_list = this.props.mayabatch_items;
        await api.maya_layer_process(record, index).then((response)=>{
            let new_record = {...record, ...response.data}
            file_list.splice(index, 1, new_record)
        })
        this.props.set_mayabatch_items(file_list)
    }
    
    removeThis(record) {
        let file_list = this.props.mayabatch_items;
        file_list.splice(record.key, 1);
        let new_file_list = file_list.map((item, index)=>{
            return {...item, key: index, id: index+1}
        })
        this.props.set_mayabatch_items(new_file_list)
    }

    async upload(e) {
        let result = await remote.dialog.showOpenDialog({
            properties: ['openFile', 'multiSelections'],
        });
        let file_list = [];
        for (let i = 0; i < result.filePaths.length; i++) {
            let file_data = {
                key: i,
                id: i + 1,
                name: result.filePaths[i],
                status: '就绪'
            }
            file_list.push(file_data)
        }
        this.props.set_mayabatch_items(file_list)
    }

    clearlist(){
        this.props.set_mayabatch_items([])
    }

    change_project(value) {
        this.props.set_mayabatch_filters(value)
    }

    render() {
        return (
            <div>
                <Row>
                    <Col span={6}>
                        <Select
                            options={this.props.project_list}
                            defaultValue={this.props.mayabatch_filters}
                            onChange={(value)=>{this.change_project(value)}}
                            style={{ margin: 12, width: 140 }} />
                            <Button onClick={(e)=>{this.upload(e)}} style={{ margin: 12 }}>选择文件</Button>
                    </Col>
                    <Col span={6} offset={12}>
                        <Button style={{ margin: 12 }} onClick={()=>{this.clearlist()}}>清空</Button>
                        <Button style={{ margin: 12 }}>全部开始</Button>
                    </Col>
                </Row>
                <Table
                    tableLayout={"fixed"}
                    dataSource={this.props.mayabatch_items}
                    columns={this.columns}
                    pagination={false}
                />
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(BatchTableForMaya);