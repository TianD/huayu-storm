import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Table, Button, Select, Row, Col } from 'antd';
import { PlayCircleTwoTone, RestTwoTone } from '@ant-design/icons';
import {set_mayabatch_filters, set_mayabatch_items} from '../actions/mayabatch';
import api from '../api'

// const { Dragger } = Upload;

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
                width: 60
            },
            {
                title: '文件',
                dataIndex: 'name',
                key: 'Name',
            },
            {
                title: '状态',
                dataIndex: 'status',
                key: 'status',
            },
            {
                title: 'Action',
                dataIndex: 'action',
                key: 'action',
                width: 140,
                render: (text, record, index) => (
                    <span>
                        <Button onClick={()=>{this.playThis(record, index)}} 
                        style={{ margin: 3 }} ghost shape="circle" icon={<PlayCircleTwoTone twoToneColor="#52c41a" />} />
                        <Button onClick={()=>{this.removeThis(record, index)}} 
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
    
    async playAll() {
        let shots = this.props.mayabatch_items;
        let new_shots = [];
        for (let i = 0; i < shots.length; i++) {
            await api.maya_layer_process(shots[i]).then((response) => {
                new_shots.push({ ...shots[i], ...response.data })
            })
        }
        this.props.set_mayabatch_items(new_shots)
    }

    removeThis(record, index) {
        let file_list = this.props.mayabatch_items;
        file_list.splice(record.key, 1);
        let new_file_list = file_list.map((item, index)=>{
            return {...item, key: index, id: index+1}
        })
        this.props.set_mayabatch_items(new_file_list)
    }

    upload(result) {
        let file_list = [];
        for (let i = 0; i < result.length; i++) {
            let file_data = {
                key: i,
                id: i + 1,
                name: result[i],
                project: this.props.mayabatch_filters,
                status: 'Ready',
            }
            file_list.push(file_data)
        }
        this.props.set_mayabatch_items(file_list)
    }

    clearlist(){
        this.props.set_mayabatch_items([])
    }

    change_project(value) {
        let files = this.props.mayabatch_items;
        let new_files = [];
        for (let i = 0; i < files.length; i++) {
            new_files.push({...files[i], project: value})
        }
        this.props.set_mayabatch_items(new_files)
        this.props.set_mayabatch_filters(value)
    }

    beforeUpload(filetype, filepromise) {
        let result = filepromise.map((item)=>(item.path))
        this.upload(result)
    }
    
    async onClick(e) {
        let result = await remote.dialog.showOpenDialog({
            properties: ['openFile', 'multiSelections'],
        });
        this.upload(result.filePaths);
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
                            <Button onClick={(e)=>{this.onClick(e)}} style={{ margin: 12 }}>选择文件</Button>
                    </Col>
                    <Col span={6} offset={12}>
                        <Button style={{ margin: 12 }} onClick={()=>{this.clearlist()}}>清空</Button>
                        <Button style={{ margin: 12 }} onClick={()=>{this.playAll()}}>全部开始</Button>
                    </Col>
                </Row>
                {/* <Dragger
                showUploadList={false}
                multiple={true}
                openFileDialogOnClick={false}
                beforeUpload={(filetype, filepromise)=>this.beforeUpload(filetype, filepromise)}> */}
                <Table
                    tableLayout={"fixed"}
                    dataSource={this.props.mayabatch_items}
                    columns={this.columns}
                    pagination={false}
                    size="small"
                    bordered
                />
                {/* </Dragger> */}

            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(BatchTableForMaya);