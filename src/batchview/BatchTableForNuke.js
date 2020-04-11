import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Table, Row, Col, Radio, Cascader, Button } from 'antd';
import { PlayCircleTwoTone, RestTwoTone } from '@ant-design/icons';
import { set_nukebatch_filters, set_nukebatch_taskid } from '../actions/nukebatch'

function mapStateToProps(state) {
    return {
        project_list: state.project_list,
        get_project_list_failed: state.get_project_list_failed,
        get_project_list_loading: state.get_project_list_loading,
        nukebatch_filters: state.nukebatch_filters,
        nukebatch_taskid: state.nukebatch_taskid
    }
}

function mapDispatchToProps(dispatch) {
    return {
        set_nukebatch_filters: (data) => dispatch(set_nukebatch_filters(data)),
        set_nukebatch_taskid: (data) => dispatch(set_nukebatch_taskid(data))
    }
}

class BatchTableForNuke extends Component {

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
                title: '预览',
                dataIndex: 'thumbnail',
                key: 'thumbnail',
                render: (text) => <image src={text} />
            },
            {
                title: '镜头',
                dataIndex: 'shot',
                key: 'shot'
            },
            {
                title: '任务类型',
                dataIndex: 'taskType',
                key: 'taskType'
            },
            {
                title: 'Action',
                dataIndex: 'action',
                key: 'action',
                render: (text, record) => (
                    <span>
                        <Button onClick={()=>this.playThis(record) }style={{ margin: 3 }} ghost shape="circle" icon={<PlayCircleTwoTone twoToneColor="#52c41a" />} />
                        <Button onClick={()=>this.removeThis(record) }style={{ margin: 3 }} ghost shape="circle" icon={<RestTwoTone twoToneColor="#eb2f96" />} />
                    </span>
                )
            }
        ] 
        this.state = {
            shots:[],
        }
    }

    changeTask(e) {
        this.props.set_nukebatch_taskid(e.target.value)
    }

    playThis(record) {
        // TODO: 用maya进行处理
        console.log(record)
    }
    
    removeThis(record) {
        let {file_list} = this.state;
        file_list.splice(record.key, 1);
        let new_file_list = file_list.map((item, index)=>{
            return {...item, key: index, id: index+1}
        })
        this.setState({
            file_list: new_file_list
        })
    }

    filterShots(value){
        this.props.set_nukebatch_filters(value)
        let dataSource = [
            {
                key: '1',
                id: 1,
                status: '就绪',
                shot: 'EP509_s001_cp_001.nk',
                thumbnail: "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png",
                taskType: 'Nuke模板',
            },
            {
                key: '2',
                id: 2,
                status: '就绪',
                shot: 'EP509_s002_cp_001.nk',
                thumbnail: "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png",
                taskType: 'Nuke模板',
            },
        ]
        this.setState({
            shots: dataSource
        })
    }

    render() {
        let {shots} = this.state;
        return (
            <div>
                <Row>
                    <Col span={6}>
                        <Cascader
                            placeholder="选择项目"
                            options={this.props.project_list}
                            defaultValue={this.props.nukebatch_filters}
                            onChange={(value)=>{this.filterShots(value)}}
                            style={{ margin: 12 }} />
                    </Col>
                    <Col span={6} offset={6}>
                        <Radio.Group value={this.props.nukebatch_taskid} onChange={(e)=>{this.changeTask(e)}} style={{ margin: 17 }}>
                            <Radio value={1} >生成Nuke工程</Radio>
                            <Radio value={2} >提交渲染</Radio>
                        </Radio.Group>

                    </Col>
                    <Col span={6}><Button style={{ margin: 12 }}>全部开始</Button></Col>
                </Row>
                <Table
                    tableLayout={"fixed"}
                    dataSource={shots}
                    columns={this.columns}
                    pagination={false}
                />
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(BatchTableForNuke)