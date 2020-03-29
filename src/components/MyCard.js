import React, {Component} from 'react';
import {Button, Card, Col, Row} from 'antd';
import {PictureOutlined} from '@ant-design/icons';
import api from '../api'

const {Meta} = Card;

class MyCard extends Component {

    componentDidMount() {

    }

    render() {
        return (
            <Card
                hoverable
                style={{width: 300, height: 144.75, margin: (10, 10, 10, 10)}}
                type={"inner"}
                cover={
                    <div>
                        <img
                            style={{width: "auto", maxHeight: 93.75, alignItems: "center"}}
                            alt="example"
                            src={api.get_thumbnail_url(this.props.shot)}
                        />
                    </div>
                }
                onClick={(event) => this.props.onClick(event)}
            >
                <Meta title={this.props.shot["label"]}/>
            </Card>
        )
    }
}

export default MyCard